# -*- coding: utf-8 -*-
import codecs, re, glob, os
resource_dir = os.getcwd() + "/txts/"
res_dir = os.getcwd() + "/results/synSplit/"

def remove_empty_pars(pars):
    res = []
    for p in pars:
        p = p.replace(u"\r",u"")
        p = p.replace(u"\n",u"")
        if u"\r" in p:
            print p
        if len(p) > 0:
            res.append(p)
    return res

def split_by_par(filename, max_chunk_len, num_of_files):
    pars = remove_empty_pars(codecs.open(resource_dir+filename, "r", "utf-8").read().split(u"\n"))
    cur_resdir = res_dir + str(max_chunk_len)
    print cur_resdir

    if not os.path.exists(cur_resdir):
        os.makedirs(cur_resdir)

    for i in range(min(num_of_files,(len(pars)/max_chunk_len))):
        cur_filename = cur_resdir + "/" +str(i)+".txt"
        print cur_filename
        if not os.path.isfile(cur_filename):
            par_start = i*max_chunk_len
            par_end = par_start + max_chunk_len
            cur_file = codecs.open(cur_filename, "w", "utf-8")
            cur_file.write(u" ".join(pars[par_start:par_end]))
            cur_file.close()





if __name__ == "__main__":
    split_by_par("AtakaNaDiskurs.txt",25,200)