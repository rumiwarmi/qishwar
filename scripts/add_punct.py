#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import csv
import re
from ast import literal_eval

# Paramètres
param=sys.argv
if len(param) < 2:
	print("File name missing.\n")
	exit(1)


csv_output = open('gold_punct.csv', 'w', newline='')
csv_writer = csv.writer(csv_output, delimiter="\t")

with open(param[1], newline='') as f:
  csvreader = csv.reader(f, delimiter='\t')
  next(csvreader)
  for row in csvreader:
	  # Phrase texte brut
	  sentence_raw = row[0]
	  print(sentence_raw)

	  # Analyse gold
	  gold = row[1].strip()
	  gold = gold.replace('][', '.')
	  gold = list(literal_eval(gold))

	  # Analyse auto
	  analyse = row[2].strip()
	  analyse = analyse.replace('][', '.')
	  analyse = list(literal_eval(analyse))


	  # Tokens
	  punct = [',', '.', '?', '!', "'", '"', '“', '”', ':','‘','’', ';', '—']
	  sentence = sentence_raw
	  for p in punct:
		  sentence = sentence.replace(p, ' ' + p + ' ')
	  sentence = re.sub(' +', ' ', sentence)
	  sentence = sentence.strip()

	  tokens = sentence.split(' ')


	  # Listes de sortie
	  gold_output = []
	  analyse_output = []

	  i = 0
	  for tok in tokens:
	  	if tok in punct:
	  		gold_output.append([tok + '[PUNCT]'])
	  		analyse_output.append([tok + '[PUNCT]'])
	  	else:
	  		gold_output.append(gold[i])
	  		analyse_output.append(analyse[i])
	  		i += 1

	  csv_writer.writerow([sentence_raw, gold_output, analyse_output])
