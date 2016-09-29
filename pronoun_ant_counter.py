__author__ = 'Hadzik'
import  os, pickle
from Metrics import *
RESOURCE_DIR = os.getcwd() + "/txts/"
RES_DIR = os.getcwd() + "/results/rucoref/"

#takes as input dictionary with format from Metrics
def count_pron_ants(rucoref = {}):
    pron_ants = 0
    all_prons = 0
    for doc in rucoref.keys():
        print doc
        all_prons += len(rucoref[doc])
        for chain in rucoref[doc]:
            if len(chain) >= 2 and isinstance(chain[-2], Pron):
                pron_ants += 1
    return all_prons, pron_ants

if __name__ == "__main__":
    if os.path.isfile(RESOURCE_DIR + "rucoref_dict_dump.pkl"):
        pkl_load = open(RESOURCE_DIR + "rucoref_dict_dump.pkl", 'rb')
        rucoref_dump = pickle.load(pkl_load)
        pkl_load.close()
    print count_pron_ants(rucoref_dump)
