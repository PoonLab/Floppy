# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 10:53:32 2020

@author: Gal
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold, \
    RepeatedStratifiedKFold, StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from statistics import mean
from sklearn.metrics import mean_squared_error, mean_absolute_error, make_scorer, matthews_corrcoef, recall_score, \
    confusion_matrix, accuracy_score, roc_auc_score, f1_score
import pickle
from pathlib import Path
import csv
from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.pipeline import Pipeline
from sklearn import tree
import joblib
import pydotplus
import collections
import argparse


parser = argparse.ArgumentParser("Random forest classifier on intrinsic disorder predictor outputs")
parser.add_argument("path", type=str, help="Path to directory containing CSV outputs of wrapper scripts.")
parser.add_argument("out", type=str, help="Filename to export model as a pickle.", default="disorder_rf.pkl")
parser.add_argument("--seed", default=211, type=int, help="optional, set random seed.")
args = parser.parse_args()

pd.set_option('display.max_columns', 500)
#% matplotlib inline

# make list of all merged csvs
files = []
for path in Path(args.path).rglob('DP*.csv'):
    files.append(path)

# drop proteins with missing data / are linearly dependent
proteins = []
for i, path in enumerate(files):
    protein = pd.read_csv(path)
    protein = protein.drop(protein.columns[[0, 1]], axis=1)
    protein = protein.drop(
        ['PredictProtein-NORSnet', 'PredictProtein-PROFbval', 'PredictProtein-Ucon',
         'PredictProtein-MD_raw'],
        axis=1, errors='ignore')
    proteins.append(protein)

for i, protein in enumerate(proteins):
    df_total = protein.merge(proteins[i])

X = df_total.drop('Disprot Label', axis=1)
y = df_total['Disprot Label']

# randomly selected seed from the 10 previous runs
np.random.seed(args.seed)

sss = StratifiedShuffleSplit(n_splits=1, train_size=0.6, random_state=args.seed)

for train_index, test_index in sss.split(X, y):
    Xtrain, Xtest = X.loc[train_index], X.loc[test_index]
    ytrain, ytest = y.loc[train_index], y.loc[test_index]

rf_pipeline = Pipeline([
    ('sampling', SMOTE(random_state=args.seed)),
    ('scaler', StandardScaler(with_mean=True, with_std=True)),
    ('rforest', RandomForestClassifier())
])
grid = {'rforest__n_estimators': [100, 200, 300, 1000],
        'rforest__min_samples_split': [2, 8, 10, 12],
        'rforest__min_samples_leaf': [1, 3, 4, 5],
        'rforest__max_depth': [None, 80, 90, 100, 110]
        }

search_rf = GridSearchCV(rf_pipeline,
                         param_grid=grid,
                         scoring=make_scorer(f1_score, average="weighted"),
                         cv=5)

search_rf.fit(Xtrain, ytrain)

print('CV f1 score for rforest model:', search_rf.best_score_.round(3))

rf = RandomForestClassifier(
        n_estimators=search_rf.best_params_['rforest__n_estimators'],
        min_samples_split=search_rf.best_params_['rforest__min_samples_split'],
        min_samples_leaf=search_rf.best_params_['rforest__min_samples_leaf'],
        max_depth=search_rf.best_params_['rforest__max_depth']
)

# fit on all training data
rf_model = rf.fit(Xtrain, ytrain)

# predict on test data
ypred = rf_model.predict(Xtest)


# compute sensitivity and specificity
tn, fp, fn, tp = confusion_matrix(ytest, ypred).ravel()
spec = tn / (tn + fp)
sens = tp / (tp + fn)
acc = (tp + tn) / (tn + fp + fn + tp)

print(tp, fp, tn, fn)

print('Model sensitivity:', sens.round(3))
print('\nModel specificity:', spec.round(3))
print('\nModel accuracy:', acc.round(3))

# calculate mcc
mcc = matthews_corrcoef(ytest, ypred)
mcc = round(mcc, 3)
print('\nModel MCC:', mcc)

# export model
# pickle.dump(rf_model, open(filename, 'wb'))
joblib.dump(rf_model, args.out)

# plot feature importance
feature_importance = rf_model.feature_importances_

indices = np.argsort(feature_importance)
fig = plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
pos = np.arange(indices.shape[0]) + 0.5
plt.barh(pos, feature_importance[indices], align='center')
plt.yticks(pos, np.array(Xtrain.columns)[indices])

# save fig
figname = f"{args.seed}-{mcc}.png"
plt.savefig(figname, format='png')


# viz decision trees
estimator1 = rf_model.estimators_[20]
estimator2 = rf_model.estimators_[40]
estimator3 = rf_model.estimators_[60]

colours = ('blue', 'red')

# Export as dot file
dot_data1 = tree.export_graphviz(estimator1,
                feature_names = Xtrain.columns,
                class_names = ['Ordered', 'Disordered'],
                rounded = True, proportion = False,
                precision = 2, filled = True)
graph1 = pydotplus.graph_from_dot_data(dot_data1)
edges1 = collections.defaultdict(list)
for edge in graph1.get_edge_list():
    edges1[edge.get_source()].append(int(edge.get_destination()))

for edge in edges1:
    edges1[edge].sort()
    for i in range(2):
        dest = graph1.get_node(str(edges1[edge][i]))[0]
        dest.set_fillcolor(colours[i])

graph1.write_png('tree1.png')

# tree 2
dot_data2 = tree.export_graphviz(estimator2,
                feature_names = Xtrain.columns,
                class_names = ['Ordered', 'Disordered'],
                rounded = True, proportion = False,
                precision = 2, filled = True)
graph2 = pydotplus.graph_from_dot_data(dot_data2)
edges2 = collections.defaultdict(list)
for edge in graph2.get_edge_list():
    edges2[edge.get_source()].append(int(edge.get_destination()))

for edge in edges2:
    edges2[edge].sort()
    for i in range(2):
        dest = graph2.get_node(str(edges2[edge][i]))[0]
        dest.set_fillcolor(colours[i])
graph2.write_png('tree2.png')

# tree 3
dot_data3 = tree.export_graphviz(estimator3,
                feature_names = Xtrain.columns,
                class_names = ['Ordered', 'Disordered'],
                rounded = True, proportion = False,
                precision = 2, filled = True)
graph3 = pydotplus.graph_from_dot_data(dot_data3)
edges3 = collections.defaultdict(list)
for edge in graph3.get_edge_list():
    edges3[edge.get_source()].append(int(edge.get_destination()))

for edge in edges3:
    edges3[edge].sort()
    for i in range(2):
        dest = graph3.get_node(str(edges3[edge][i]))[0]
        dest.set_fillcolor(colours[i])
graph3.write_png('tree3.png')
# # Convert to png using system command
# from subprocess import call
# call(['dot', '-Tpng', 'tree1.dot', '-o', 'tree1.png', '-Gdpi=600'])
#
# from subprocess import call
# call(['dot', '-Tpng', 'tree2.dot', '-o', 'tree2.png', '-Gdpi=600'])
#
# from subprocess import call
# call(['dot', '-Tpng', 'tree3.dot', '-o', 'tree3.png', '-Gdpi=600'])


