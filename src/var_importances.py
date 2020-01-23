import os
from glob import glob1
import csv

import pickle as pkl
import pandas as pd


files = glob1(os.getcwd(), "models*")
varns = ["_".join(fl.split(".")[0].split('_')[1:]) for fl in files]



for fh, varn in zip(files, varns):
    if 1:

        if varn == "tot_p":
            from rforest_test2 import feat_list
        else:
            from rforest_test import feat_list

        with open(fh, "rb") as fhand:
            models = pkl.load(fhand)
        
        if varn == 'occ_p':
            SELECT_CRITERION = 60.0
        elif varn in ['avail_p', 'total_p']:
            SELECT_CRITERION = 75.0
        elif varn in ['inorg_p', 'org_p']:
            SELECT_CRITERION = 70.0
        elif varn == 'tot_p':
            SELECT_CRITERION = 65.0
        
        models = [m1 for m1 in models if m1[1] >= SELECT_CRITERION]
        
        with open("importances_%s.csv" % varn, mode="w") as csvfile:
            fwriter = csv.DictWriter(csvfile, fieldnames=feat_list)
            fwriter.writeheader()

            for model in models:
                rf = model[2]
                importances = list(rf.feature_importances_)

                # List of tuples with variable and importance
                feature_importances = [(feat, importance) for feat, importance in zip(feat_list, importances)]
                print(dict(feature_importances))
                fwriter.writerow(dict(feature_importances))