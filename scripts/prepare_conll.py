import sys
import csv
import os
from pathlib import Path
from ast import literal_eval
import re

"""
Input file format : CSV (que | spa | sent_id | morpho_analyse | corresp_morph_lemma)

"""

PUNCT = ['...', ',', '.', '?', '!', "'", '"', '“', '”', ':','‘','’', ';', '— ', '—', '–', '…', '¡', '¿']

def tokenise(sent):
	for p in PUNCT:
		sent = sent.replace(p, ' ' + p)

	sent = sent.replace('  ', ' ')
	return sent.split(' ')

def find_enclitics(morph_w_tag_list):
	enclitics = ["mi[Asrt]", "shi[Nfh]", "pis[Coord]", "tsu[Neg]", "ku[Inter]", "lla[Lim]", "qa[Top]", "ri[Emp]", "raq[Inacp]"]

	return [elem for elem in morph_w_tag_list if elem in enclitics]


# Renvoie la dernière classe grammaticale présente dans le token
def find_root(morph_w_tag_list):
	roots = ['\[N\]', '\(N\)', '\(V\)', 'VTr', 'VInt', '\[ADV\]', '\(ADV\)', '\[ADJ\]', '\[DET\]', '\[PRON\]', '\[NUM\]', '\[ADP\]', '\[SCONJ\]', '\[CCONJ\]', '\[INTJ\]']
	compiled_roots = [re.compile(p) for p in roots]

	for mt in morph_w_tag_list:
		for p in compiled_roots:
			match = p.search(mt)
			if match:
				pos_tag = match.group(0)

	pos_tag = pos_tag.replace('[', '').replace(']', '')
	pos_tag = pos_tag.replace('(', '').replace(')', '')

	if pos_tag == 'N':
		pos_tag = 'NOUN'
	elif pos_tag == 'V' or pos_tag == 'VTr' or pos_tag == 'VInt':
		pos_tag = 'VERB'

	return pos_tag

def get_lemma(morph_tag):
	parts = morph_tag.split('[', 1)
	morph = parts[0]
	return morph

# Paramètres
param=sys.argv
if len(param) < 2:
	print("File name missing.\n")
	exit(1)

filename = param[1]
dirname = os.path.dirname(filename)
outputname = os.path.join(dirname, str(Path(filename).stem) + '.conll')


with open(outputname, 'w', newline='') as output:
	sentwriter = csv.writer(output, delimiter='\t')

	with open(filename, 'r', newline='') as f:
		sentreader = csv.reader(f, delimiter='\t')
		for row in sentreader:
			sent_que = row[0]
			sent_spa = row[1]
			sent_id = row[2]
			morpho_analyse = literal_eval(row[3])

			sentwriter.writerow(['sent_id = ' + sent_id])
			sentwriter.writerow(['text = ' + sent_que])
			sentwriter.writerow(['gloss = '])
			sentwriter.writerow(['spa = ' + sent_spa])
			sentwriter.writerow(['eng = '])


			tokens = tokenise(sent_que)

			i = 0 # position token
			idx = 1 # index conll
			conll_lines = []
			for tok in tokens:
				if tok in PUNCT:
					sentwriter.writerow([idx, tok, tok, 'PUNCT', '_', '_', '_', '_', '_', '_'])
					idx += 1
				else:
					token_analyse = morpho_analyse[i][0]
					morph_w_tag_list = token_analyse.split('+')
					enclitics = find_enclitics(morph_w_tag_list)
					if enclitics:
						j = idx + len(enclitics)
						sentwriter.writerow([str(idx) + '-' + str(j), tok, '_', '_', '_', '_', '_', '_', '_', '_'])
						sentwriter.writerow([idx, tok, '_', find_root(morph_w_tag_list), '_', '_', '_', '_', '_', '_'])
						for enc in enclitics:
							idx += 1
							sentwriter.writerow([idx, '_', get_lemma(enc), 'PART', '_', '_', '_', '_', '_', '_'])
							
					else:
						sentwriter.writerow([idx, tok, '_', find_root(morph_w_tag_list), '_', '_', '_', '_', '_', '_'])
					
					idx += 1
					i += 1
