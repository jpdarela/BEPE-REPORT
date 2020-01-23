import os
import pickle as pkl
import multiprocessing as mp
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor


pfracs = ["occ_p", "mineral_p", "inorg_p", "org_p", "avail_p", "total_p"]
label_name = pfracs[0]

features = pd.read_csv("p_fractions-final.csv")
# # Choose the important _features 

feat_used = ["lat", "lon", "s_type2", "sand", "silt", "clay", "slope", "elev", "MAT", "MAP",
             "pH", "tot_OC", "tot_N", label_name]

clean_data = features[feat_used]

# # OTHER variables to predict in dataset IN THE DATASET:

# # TODO predict the lab fractions and include N and C in soil 
### OK

# # One-hot encoding for nominal variables ('s_type2')
dta = pd.get_dummies(clean_data)

# Variable to be predicted as an np.array
labels = np.array(dta[label_name])

# Exclude labels from features
feat = dta.drop(label_name, axis=1)

# Get the features names
feat_list = list(feat.columns)

# Transform in a NP.array
feat = np.array(feat)

# TEST some random STATES
# mETHOD

def chunks(lst, chunck_size):
    from random import shuffle
    shuffle(lst)
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), chunck_size):
        yield lst[i:i + chunck_size]

def make_model(index):
    method = 'rf' # clf
#for index in np.random.randint(0,10000, 500):
    # Divide in train and testing datasets
    train_features, test_features, train_labels, test_labels = train_test_split(feat, labels, test_size = 0.30, random_state = index)

    # pandasCreate the random forest
    rf = RandomForestRegressor(n_estimators=1500, criterion="mse", n_jobs= 1, random_state = index)
    
    # ADA BOOSTING - NOT SO GOOD
    # rf = AdaBoostRegressor(random_state=index, n_estimators=1000)

    # GRADIENT BOOST REGRESSOR
    if method == "clf":
        params = {'n_estimators': 1500, 'max_depth': 5, 'min_samples_split': 2,
                  'learning_rate': 0.01, 'loss': 'ls'}
        clf = GradientBoostingRegressor(**params)

    if method == 'rf':
        rf.fit(train_features, train_labels)
    elif method == 'clf':
        clf.fit(train_features, train_labels)
        rf = clf

    # Use the forest's predict method on the test data
    predictions = rf.predict(test_features)
    # Calculate the absolute errors
    errors = abs(predictions - test_labels)

    # # Print out the mean absolute error (mae)
    # print("\n\nINDEX: ", index, "\n")
    # print('Mean Absolute Error:', round(np.mean(errors), 2), 'mg/kg')

    # Calculate mean absolute percentage error (MAPE)
    mape = 100 * (errors / test_labels)
    # Calculate and display accuracy
    accuracy = 100 - np.mean(mape)
    # print('Accuracy:', round(accuracy, 2), '%.')

    if accuracy >= 60.0:
        #good_models["model%d" %index] = rf
        return (index, accuracy, rf)
    else: return None

    # importances = list(rf.feature_importances_)
    # # List of tuples with variable and importance
    # feature_importances = [(feat, round(importance, 5)) for feat, importance in zip(feat_list, importances)]

    # feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)

    # [print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances]

if __name__ == "__main__":
    result = []
    for lst in chunks(np.arange(1,100000), 10000):
        with mp.Pool(processes=128) as pool:
            result += pool.map(make_model,lst)

    models = [a for a in result if a is not None]
    with open("models_%s.pkl" %label_name, mode="wb") as fh:
        pkl.dump(models, fh)
    os.system("ipython write_raster.py")
