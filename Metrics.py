__author__ = 'Hadzik'
import codecs, os, re, pickle, glob
from lxml import etree

RESOURCE_DIR = os.getcwd() + "/txts/"
RES_DIR = os.getcwd() + "/results/rucoref/"
PRON_TYPES = [u"pron", u"poss"]


class Ant(object):
    start = -1
    end = -1
    chain_id = -1
    group_id = -1

    def __init__(self, start, end, chain_id=-1, group_id=-1):
        self.start = start
        self.end = end
        self.chain_id = chain_id
        self.group_id = group_id

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_chain_id(self):
        return self.chain_id

    def get_group_id(self):
        return self.group_id

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.start == other.start)

    def __ne__(self, other):
        return not self.__eq__(other)


class Pron(Ant):
    type = "TYPE"
    antecedent = None

    def unify_type(self, type):
        if type.islower():
            type = type.replace(u"pron", u"PERSONAL")
            type = type.replace(u"poss", u"PERSONAL")
        return type

    def __init__(self, start, end, type, antec, chain_id=-1, group_id=-1):
        super(Pron, self).__init__(start, end, chain_id, group_id)
        self.type = self.unify_type(type)
        self.antecedent = antec

    def get_ant_start(self):
        return self.antecedent.get_start()

    def get_ant_end(self):
        return self.antecedent.get_end()

    def has_ant(self):
        return True if self.antecedent is not None else False


# finds an antecedent in a list of previous Ants
def find_antec(group_id, prev_ants):
    for a in prev_ants:
        if a.get_group_id() == group_id:
            return a


def form_pron_chain(pron, prev_ants):
    res = []
    for a in prev_ants:
        if a.get_chain_id() == pron.get_chain_id():
            res.append(a)
    res.append(pron)
    return res


# makes a dictionary (doc_id:[[Ant, Ant, Ant, Pron]])
def parse_rucoref(corpus_path):
    rucoref = [l.split(u"\t") for l in codecs.open(RESOURCE_DIR + corpus_path, "r", "utf-8")]
    res = {}
    prev_ants = []
    value_chains = []
    prev_doc = 1
    for r in rucoref:
        if r[0] == u"doc_id":
            continue
        key_doc = int(r[0])
        if key_doc != prev_doc:
            res[prev_doc] = value_chains
            value_chains = []
        group = int(r[2])
        chain = int(r[3])
        link = int(r[4])
        start = int(r[5])
        end = start + int(r[6])
        re_type = re.search(u"str:([^|]+)", r[9])
        ant_type = u""
        if re_type is not None:
            ant_type = re_type.group(1)
        if ant_type in PRON_TYPES:
            pron = Pron(start, end, ant_type, find_antec(link, prev_ants), chain, group)
            value_chains.append(form_pron_chain(pron, prev_ants))
            prev_ants.append(pron)
        else:
            prev_ants.append(Ant(start, end, chain, group))
        prev_doc = key_doc
    return res


# makes list of all Pron-objects in this file
def parse_one_xml(filename):
    tree = etree.parse(filename)
    res = []
    all_ants = tree.xpath('.//I-annotation[contains(@class,"Antecedent")]')
    all_anaphors = tree.xpath('.//I-annotation[contains(@class,"Anaphor")]')
    for an in all_anaphors:
        start = int(an.xpath('start')[0].text)
        end = int(an.xpath('end')[0].text)
        value = an.xpath('value')[0]
        ant = Ant(int(value.xpath('antecedent/start')[0].text), \
                      int(value.xpath('antecedent/end')[0].text))
        res.append(Pron(start, end, "", ant))
    return res


# makes a dictionary (doc_id:[Pron, Pron])
def parse_texterra_output(dirpath):
    all_xmls = glob.glob(RESOURCE_DIR + dirpath + "*.txt")
    res = {}
    for f in all_xmls:
        key_doc = int(re.search("/(\d+)\.txt", f).groups(1)[0])
        res[key_doc] = parse_one_xml(f)
    return res


# compares system output with GOLD chain: lenient assessment
def compare_anaphora(pron, chain):
    gold_pron = chain[-1]

    if not pron.has_ant() and not gold_pron.has_ant():
        return True

    if not pron.has_ant() or not gold_pron.has_ant():
        return False
    p_start = pron.get_ant_start()
    g_start = gold_pron.get_ant_start()
    p_end = pron.get_ant_end()
    g_end = gold_pron.get_ant_end()

    if rough_compare(p_start,g_start) or rough_compare(p_end, g_end) or\
            (g_start < p_start and p_end < g_end):
        return True
    for prev_ant in chain:
        if rough_compare(p_start,prev_ant.get_start()) or rough_compare(p_end, prev_ant.get_end()) or\
            (prev_ant.get_start() < p_start and p_end < prev_ant.get_end()):
            return True
    return False


#workaround for shift-counts fuckups
def rough_compare(left, right):
    dif_start = abs(left - right)
    if dif_start == 0:
        return True
    elif dif_start == 1:
        return True
    return False

# counts true links, false and unresolved pronouns in document
def count_t_f_unfound(texterra_doc, rucoref_doc, doc_id):
    true_links = 0
    false_links = 0
    unresolved = 0
    unfound = len(rucoref_doc) - len(texterra_doc)
    not_in_gold = 0

    for pron in texterra_doc:
        if len(rucoref_doc) == 0:
            unfound += 1
            not_in_gold += 1
        for i in range(len(rucoref_doc)):
            assert isinstance(rucoref_doc[i][-1], Pron)
            if rough_compare(rucoref_doc[i][-1].get_start(),pron.get_start()):
                is_true = compare_anaphora(pron, rucoref_doc[i])
                true_links += is_true
                false_links += not is_true
                rucoref_doc.remove(rucoref_doc[i])
                if not pron.has_ant() and is_true == False:
                    unresolved += 1
                break
            if i == len(rucoref_doc) - 1:
                unfound += 1
                not_in_gold += 1
    # for i in rucoref_doc:
    #     print i[-1].get_start()

    assert true_links + false_links + not_in_gold == len(texterra_doc)

    return true_links, false_links, unfound, unresolved


def calculate_metrics(texterra, rucoref):
    all_true = 0
    all_false = 0
    all_unfound = 0
    all_unresolved = 0
    all_gold = 0

    for doc_id in texterra.keys():
        if rucoref.has_key(doc_id):
            print doc_id
            if(doc_id == 714):
                stop = True
            all_gold += len(rucoref[doc_id])
            true_links, false_links, unfound, unresolved = \
                count_t_f_unfound(texterra[doc_id], rucoref[doc_id], doc_id)
            all_true += true_links
            all_false += false_links
            all_unfound += unfound
            all_unresolved += unresolved

    precision = all_true/(all_true+all_false + 0.0)
    recall = all_true/(all_gold + 0.0)
    f_measure = 2*precision*recall/(precision + recall)

    return round(precision,2), round(recall,2), round(f_measure,2), all_unfound, all_unresolved



if __name__ == "__main__":
    if os.path.isfile(RESOURCE_DIR + "rucoref_dict_dump.pkl"):
        pkl_load = open(RESOURCE_DIR + "rucoref_dict_dump.pkl", 'rb')
        rucoref_dump = pickle.load(pkl_load)
        pkl_load.close()
    else:
        rucoref_dump = parse_rucoref("rucoref/Groups_wo_d.txt")
        file_dump = open(RESOURCE_DIR + 'rucoref_dict_dump.pkl', 'wb')
        pickle.dump(rucoref_dump, file_dump)
        file_dump.close()

    print calculate_metrics(parse_texterra_output("rucoref_out_new/"), rucoref_dump)

    # test = parse_texterra_output("rucoref_out/")
    # for i in range(1, 5):
    #     print i
    #     if (test.has_key(i)):
    #         for chain in test[i]:
    #             str_chain = u""
    #             str_chain += str(chain.get_start())
    #             str_chain += u" "
    #             print u"\t\t" + str_chain




