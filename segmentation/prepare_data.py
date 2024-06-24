import pandas as pd
from ast import literal_eval
import re

FILENAME = 'data_non_ambigu_SILVER.csv'

def tokenise(sent):
    punct = [',', '.', '?', '!', "'", '"', '“', '”', ':','‘','’', ';', '— ', '—', '–', '…']
    sentence = "".join(c for c in sent if c not in punct)
    s = sentence.lower()
    s = s.replace('  ', ' ')
    tokens = s.split(' ')
    return [t for t in tokens if t != '']

def generate_data(analysis):
    # Créer une liste vide pour stocker les étiquettes
    labels = []

    # Parcourir chaque token dans l'analyse
    for i, token in enumerate(analysis):
        # Parcourir chaque morphe dans le token
        for j, morpheme in enumerate(token):
            # Ajouter chaque caractère du morpheme et son étiquette correspondante
            if len(morpheme) == 1:
            # Si le morphe courant n'a qu'un seul caractère
                labels.append('U')
                continue
            for k, char in enumerate(morpheme):

                if j == 0 and k == 0:
                    # Si c'est le début du premier morpheme du token
                    labels.append('D')
                elif j == len(token) - 1 and k == len(morpheme) - 1:
                    # Si c'est la fin du dernier morpheme du token
                    labels.append('F')
                elif k == 0:
                    # Si c'est le début d'un morpheme (mais pas le premier du token)
                    labels.append('D')
                elif k == len(morpheme) - 1:
                    # Si c'est la fin d'un morpheme (mais pas le dernier du token)
                    labels.append('F')

                else:
                    # Si c'est un caractère au milieu d'un morpheme
                    labels.append('M')

    return labels


df = pd.read_csv(FILENAME, delimiter='\t', names=['SENT', 'ANALYSE', 'PAIRS', 'MORPHS'], header=None)

tokens_list = []
for sentence in df['SENT']:
    tokens_list += tokenise(sentence) # flat list of tokens

morphs_list = []
BME_list = []
for morphstr in df['MORPHS']:
    morphs_local_list = list(literal_eval(morphstr))
    morphs_list += morphs_local_list # flat list of morphs
    for elem in morphs_local_list:
        BME_list.append(generate_data([elem]))

labels_list = []
for analyse in df['ANALYSE']:
    analyse_list = list(literal_eval(analyse))
    # Extract labels from analysis
    for elem in analyse_list:
        labels = re.findall(r'\[([^\[\]]+)\]', elem[0])
        labels_list.append(labels) # flat list of analyses
    
data = pd.DataFrame()
data['TOKEN'] = tokens_list
data['MORPH'] = morphs_list
data['SEG_BME'] = BME_list
data['LABEL'] = labels_list

data.to_csv("prepared_data.csv", sep='\t', encoding='utf-8')


