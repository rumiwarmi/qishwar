import sys
import pandas as pd
import sklearn
import sklearn_crfsuite
import scipy.stats
import math, string, re

from sklearn.metrics import make_scorer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from itertools import chain
from sklearn.preprocessing import MultiLabelBinarizer

import pickle

# Code partly copied from https://towardsdatascience.com/pos-tagging-using-crfs-ea430c5fb78b

# Paramètres
param=sys.argv
if len(param) < 2:
	print("File name missing. Usage : python train_crf.py train_dir/\n")
	exit(1)

def word2features(sent, i):
    morpheme = sent[i][0]

    punct = [',', '.', '?', '!', "'", '"', '“', '”', ':','‘','’', ';', '—']

    features = {
        'bias': 1.0,
        'morpheme': morpheme,
        'len(morpheme)': len(morpheme),
        'morpheme.isdigit': morpheme.isdigit(),
        'morpheme.ispunctuation': (morpheme in punct),
        'morpheme.end_of_word': (sent[i][2] == '#'),
        'morpheme.uppercase': (sent[i][3] == 'True')
    }

    if i > 0:
        prec_morpheme = sent[i-1][0]
        features.update({
            'prec_morpheme' : prec_morpheme,
            'len(prec_morpheme)' : len(prec_morpheme),
            'prec_morpheme.isdigit': prec_morpheme.isdigit(),
            'prec_morpheme.ispunctuation': (prec_morpheme in punct),
            'prec_morpheme.end_of_word': (sent[i-1][2] == '#'),
            'prec_morpheme.uppercase': (sent[i-1][3] == 'True')
        })
    else:
        features['BOS'] = True

    if i > 1:
        pp_morpheme = sent[i-2][0]
        features.update({
            'pp_morpheme' : pp_morpheme,
            'len(pp_morpheme)' : len(pp_morpheme),
            'pp_morpheme.isdigit': pp_morpheme.isdigit(),
            'pp_morpheme.ispunctuation': (pp_morpheme in punct),
            'pp_morpheme.end_of_word': (sent[i-2][2] == '#'),
            'pp_morpheme.uppercase': (sent[i-2][3] == 'True')
        })

    if i < len(sent) - 1:
        next_morpheme = sent[i+1][0]
        features.update({
            'next_morpheme':next_morpheme,
            'len(next_morpheme)':len(next_morpheme),
            'next_morpheme.isdigit': next_morpheme.isdigit(),
            'next_morpheme.ispunctuation': (next_morpheme in punct),
            'next_morpheme.end_of_word': (sent[i+1][2] == '#'),
            'next_morpheme.uppercase': (sent[i+1][3] == 'True')
        })

    else:
        features['EOS'] = True

    if i < len(sent) - 2:
        nn_morpheme = sent[i+2][0]
        features.update({
            'nn_morpheme':nn_morpheme,
            'len(nn_morpheme)':len(nn_morpheme),
            'nn_morpheme.isdigit': nn_morpheme.isdigit(),
            'nn_morpheme.ispunctuation': (nn_morpheme in punct),
            'nn_morpheme.end_of_word': (sent[i+2][2] == '#'),
            'nn_morpheme.uppercase': (sent[i+2][3] == 'True')
        })

    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2tokens(sent):
    return [word[0] for word in sent]

def sent2labels(sent):
    return [word[1] for word in sent]


def format_data(csv_data):
    sents = []
    for i in range(len(csv_data)):
        if math.isnan(csv_data.iloc[i, 0]):
            continue
        elif csv_data.iloc[i, 0] == 1.0:
            sents.append([[csv_data.iloc[i, 1], csv_data.iloc[i, 2], csv_data.iloc[i, 3], csv_data.iloc[i, 4]]])
        else:
            sents[-1].append([csv_data.iloc[i, 1], csv_data.iloc[i, 2], csv_data.iloc[i, 3], csv_data.iloc[i, 4]])

    for sent in sents:
        for i, word in enumerate(sent):
            if type(word[0]) != str:
                del sent[i]
                print("Erreur dans le format de la phrase : {}".format(sent))
    return sents


# Chargement des données
data =  {}
data['train'] = pd.read_csv(param[1] + 'train_data.csv', sep='\t')
data['test'] = pd.read_csv(param[1] + 'test_data.csv', sep='\t')

#print(format_data(data['test']))

train_sents = format_data(data['train'])
test_sents = format_data(data['test'])

Xtrain = [sent2features(s) for s in train_sents]
ytrain = [sent2labels(s) for s in train_sents]


Xtest = [sent2features(s) for s in test_sents]
ytest = [sent2labels(s) for s in test_sents]

"""
# Entraînement du modèle
crf = sklearn_crfsuite.CRF(
    algorithm = 'lbfgs',
    c1 = 0.25,
    c2 = 0.3,
    max_iterations = 100,
    all_possible_transitions=True
)

crf.fit(Xtrain, ytrain)

# Save model
with open(param[1] + 'model.pkl','wb') as f:
    pickle.dump(crf,f)

"""
# Load model
with open(param[1] + 'model.pkl', 'rb') as f:
    crf = pickle.load(f)
    
# Compute metrics
labels = list(crf.classes_)

ypred = crf.predict(Xtrain)
print('F1 score on the train set = {}\n'.format(metrics.flat_f1_score(ytrain, ypred, average='weighted', labels=labels)))
print('Accuracy on the train set = {}\n'.format(metrics.flat_accuracy_score(ytrain, ypred)))


sorted_labels = sorted(
    labels,
    key=lambda name: (name[1:], name[0])
)
print('Train set classification report: \n\n{}'.format(metrics.flat_classification_report(ytrain, ypred, labels=sorted_labels, digits=3)))

#print(metrics.confusion_matrix(ytrain, ypred, labels=sorted_labels)


# Metrics on test set
ypred = crf.predict(Xtest)
print('F1 score on the test set = {}\n'.format(metrics.flat_f1_score(ytest, ypred, average='weighted', labels=labels)))
print('Accuracy on the test set = {}\n'.format(metrics.flat_accuracy_score(ytest, ypred)))


sorted_labels = sorted(
    labels,
    key=lambda name: (name[1:], name[0])
)
print('Test set classification report: \n\n{}'.format(metrics.flat_classification_report(ytest, ypred, labels=sorted_labels, digits=3)))

# Transition probabilities
from collections import Counter

def print_transitions(transition_features):
    for (label_from, label_to), weight in transition_features:
        print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))

print("-- Top 10 likely transitions --\n")
print_transitions(Counter(crf.transition_features_).most_common(10))

print("\n--Top 10 unlikely transitions --\n")
print_transitions(Counter(crf.transition_features_).most_common()[-10:])
