#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fichier entrée : phrases qwh/esp alignées au format csv (col 1: que, col 2: esp)
"""
import sys
import csv
from subprocess import Popen, PIPE
from shlex import split
import json
from datetime import date
import re

# Paramètres
param=sys.argv
if len(param) < 2:
	print("File name missing.\n")
	exit(1)

def runFoma(modelname, tok):
	p1 = Popen(["echo", tok], stdout=PIPE)
	p2 = Popen(["flookup", "-x", modelname], stdin=p1.stdout, stdout=PIPE)
	res = p2.communicate()[0]

	return [r for r in res.decode("utf-8").split('\n') if r != ""]

def isNumber(tok):
	return re.search("[0-9]+", tok)


""" Tokenize et analyse """

punct = [',', '.', '?', '!', "'", '"', '“', '”', ':','‘','’', ';', '— ', '—', '–', '…']
analysis = {}
failed_analysis = []
ambigu = []
nb_toks = 0
nb_formes = 0
nb_failed = 0
nb_ambiguites = 0
nb_ambiguites_guesser = 0
nb_guessed = 0


with open(param[1], 'r', newline='') as f:
	# Fichier sortie
	outputname = "analyse_" + date.today().strftime("%d-%m-%Y") + ".csv"
	output = open(outputname, 'w', newline='')
	sentwriter = csv.writer(output, delimiter='\t')

	# Parsing fichier entrée
	sentreader = csv.reader(f, delimiter='\t')
	for row in sentreader:
		sent_qwh = row[0].rstrip()
		sent_spa = row[1]
		

		tagged_sent = []

		# Tokenisation
		sentence = "".join(c for c in sent_qwh if c not in punct)
		s = sentence.lower()
		s = s.replace('  ', ' ')
		tokens = s.split(' ')
		tokens = [t for t in tokens if t != '']

		# Analyse morpho
		for tok in tokens:
			nb_toks += 1
			tok = tok.rstrip('\n')
			
			# Token pas encore analysé
			if tok not in analysis:
				nb_formes += 1

				if isNumber(tok):
					tok_analyse = tok + '[Num]'
				else:
					tok_analyse = runFoma("qwh.foma", tok)
					tok_analyse = list(set(tok_analyse))
					if len(tok_analyse) > 1:
						nb_ambiguites += 1
						ambigu.append(tok_analyse)
					elif len(tok_analyse) < 1:
						print(tokens)
						continue


				if tok_analyse[0] == "+?":

					# Guesser
					tok_analyse = runFoma("guess.foma", tok)
					if tok_analyse[0] == "+?":
						nb_failed += 1
						failed_analysis.append(tok)
						tok_analyse = [tok + '[UNK]']
					else:
						nb_guessed += 1
						if len(tok_analyse) > 1:
							nb_ambiguites_guesser += 1
							ambigu.append(tok_analyse)

				analysis[tok] = tok_analyse
			else:
				if '[UNK]' in analysis[tok][0]:
					nb_failed += 1
					failed_analysis.append(tok)
				
			
			tagged_sent.append(analysis[tok])

		sentwriter.writerow([sent_qwh, tagged_sent, sent_spa])
	print("Nb de tokens : " + str(nb_toks))
	print("Nb de mots uniques : " + str(nb_formes))
	print("Nb d'échecs : " + str(nb_failed))
	print("Nb d'ambiguïtés : " + str(nb_ambiguites))
	print("Nb d'ambiguïtés guesser : " + str(nb_ambiguites_guesser))
	print("Nb de mots devinés {}".format(nb_guessed))

	#with open("results.json", "w") as output:
	#	json.dump(analysis, output, indent=3, sort_keys=True)

	with open("failed_analysis.txt", "w") as err_out:
		for tok in failed_analysis:
			err_out.write(tok + '\n')

	with open("ambiguites.txt", "w") as ambig_out:
		for amb in ambigu:
			for a in amb:
				ambig_out.write(a + '\t')
			ambig_out.write('\n')
