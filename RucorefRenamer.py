# -*- coding: utf-8 -*-
__author__ = 'Hadzik'
import codecs, os
resource_dir = os.getcwd() + "/txts/rucoref/"
res_dir = os.getcwd() + "/results/rucoref/"

def rename(ids_filename, files):
    ids = codecs.open(resource_dir+ids_filename, "r", "utf-8")
    doc_ids = {line[0] : line[1] for line in [l.split(u"\t") for l in ids]}
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
    for f in doc_ids.keys():
        cur_file = resource_dir + files + doc_ids[f].encode('ascii')
        print cur_file
        if os.path.exists(cur_file):
            new_file = codecs.open(res_dir + f.encode('ascii') + ".txt", "w", "utf-8")
            text = codecs.open(cur_file, "r", "utf-8").read()
            new_file.write(text)
            new_file.close()


if __name__ == "__main__":
    rename("Documents.txt", "rucoref_texts/")

