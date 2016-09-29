__author__ = 'Hadzik'
import codecs, os
resource_dir = os.getcwd() + "/txts/"
res_dir = os.getcwd() + "/results/rucoref/"

def removeDeictic(filepath, deictic_list, pers_list, refl_list):
    groups = [l.split(u"\t") for l in codecs.open(resource_dir+filepath, "r", "utf-8")]

    deicts = []
    for l in codecs.open(resource_dir+deictic_list, "r", "utf-8"):
        deicts += l.split()

    pers = []
    for l in codecs.open(resource_dir+pers_list, "r", "utf-8"):
        pers += l.split()

    refl = []
    for l in codecs.open(resource_dir+refl_list, "r", "utf-8"):
        refl += l.split()

    res = codecs.open(res_dir + "Groups_wo_d.txt", "w", "utf-8")

    for g in groups:
        g[7] = g[7].lower()
        if g[7] in deicts:
            g[9] = g[9].replace(u"str:noun", u"str:deic")
            g[9] = g[9].replace(u"str:pron", u"str:deic")
            g[9] = g[9].replace(u"str:refl", u"str:deic")
            g[9] = g[9].replace(u"str:poss", u"str:deic_poss")
            if u"deic" not in g[9]:
                print g[7], g[9], groups.index(g)
        elif g[7] in pers:
            g[9] = g[9].replace(u"str:noun", u"str:pron")
            g[9] = g[9].replace(u"str:|type:", u"str:pron|type:")
            g[9] = g[9].replace(u"str:refl", u"str:pron")
            g[9] = g[9].replace(u"str:rel", u"str:pron")
            g[9] = g[9].replace(u"str:noun", u"str:pron")
            if u"pron" not in g[9] and u"poss" not in g[9]:
                print g[7], g[9], groups.index(g)
        elif g[7] in refl:
            g[9] = g[9].replace(u"str:pron", u"str:refl")
            g[9] = g[9].replace(u"str:poss", u"str:refl")
            g[9] = g[9].replace(u"str:noun", u"str:refl")
            g[9] = g[9].replace(u"str:rel", u"str:refl")
            g[9] = g[9].replace(u"str:|type:", u"str:refl|type:")
            if u"refl" not in g[9]:
                print g[7], g[9], groups.index(g)

        res.write(u"\t".join(g))

    res.close()

if __name__ == "__main__":
    removeDeictic("rucoref/Groups.txt", "deictic.txt", "personal.txt", "refl.txt")


