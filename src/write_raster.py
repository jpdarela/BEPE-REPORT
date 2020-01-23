import os
import pickle as pkl
import numpy as np
import pandas as pd

mode = 'except'
# mode = 'fractions'
# mode = 'total'

if mode == 'fractions':

    from rforest_test import feat_list
    from rforest_test import label_name
    output = "./predicted_P_%s/" % label_name
    model = "models_"
    predictors = './predict_vars.csv'

elif mode == 'total':
    
    from rforest_test2 import feat_list
    from rforest_test2 import label_name
    output = "./predictedTP_P_%s/" % label_name
    model = "modelsTP_"
    predictors = './predict_vars2.csv'


# Exception - make a manual prediction for a fraCTION
else:
    from rforest_test import feat_list
    label_name = 'total_p'
    output = "./predicted_P_%s/" % label_name
    model = "models_"
    predictors = './predict_vars.csv'

if not os.path.exists(output): os.mkdir(output) 

with open("%s%s.pkl" %(model, label_name), 'rb') as fh:
    models = pkl.load(fh)

# APPLY the model in the raster predictor variables

if label_name == 'occ_p':
    SELECT_CRITERION = 60.0
elif label_name in ['avail_p', 'total_p']:
    SELECT_CRITERION = 75.0
elif label_name in ['inorg_p', 'org_p']:
    SELECT_CRITERION = 70.0
elif label_name == 'tot_p':
    SELECT_CRITERION = 65.0

models_s = [m1 for m1 in models if m1[1] >= SELECT_CRITERION]
acc = []
out_list = []

for i, md in enumerate(models_s):
    
    # # Predictors table
    
    #map_data = pd.read_csv(predictors)[feat_list].__array__()

    #rf = md[2]

    acc.append(md[1])

    # new_column = rf.predict(map_data)
    # if len(new_column.shape) > 1:
    #     new_column = new_column[:,0]
    # # #print(model[1])
    # # #print(new_column.mean()
    # map_data = pd.read_csv(predictors)
    #print(map_data.shape)
    #print(map_data.keys())
    #print(label_name)
    # map_data[label_name] = new_column
    # map_data.to_csv(output + "/predicted_%s_model_%s.csv" % (label_name, str(md[0])), index=False, header=True)

print('number of models: ', i + 1)
print('Mean acc: ', sum(acc) / i + 1)

with open("selected_models_%s.pkl" % label_name, 'wb') as fh:
    pkl.dump(models_s, fh)
