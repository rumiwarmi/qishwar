import argparse
import re
from subprocess import Popen, PIPE

"""
This script is used to apply the Foma morphological analyser to sentences contained in a text file, whose location is passed as a parameter. By default, the guesser is activated.

Usage : python run_morpho_analyser.py FILE_PATH

Run without guesser : python run_morpho_analyser.py FILE_PATH --no-guesser

"""

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument("--output", "-o", type=str, help="Output filename")
parser.add_argument("--no-guesser", action='store_true', help="Deactivate guesser")

args = parser.parse_args()

if args.output:
	outputname = args.output
else:
	outputname = "morpho_analyse.txt"

def runFoma(modelname, tok):
	p1 = Popen(["echo", tok], stdout=PIPE)
	p2 = Popen(["flookup", "-x", modelname], stdin=p1.stdout, stdout=PIPE)
	res = p2.communicate()[0]

	return [r for r in res.decode("utf-8").split('\n') if r != ""]

def isNumber(tok):
	return re.search("[0-9]+", tok)
	

def tokenise(phrase):

	tokens = re.findall(r"[\w']+|[.,!?;:—–…“”‘’»/¿¡«]", phrase)

	return tokens

punct = [',', '.', '?', '!', "'", '"', '“', '”', ':','‘','’', ';', '— ', '—', '–', '…', '/', '¿', '¡', "«", "»"]
nb_tok = 0
forms = {}

output = open(outputname, 'w')

with open(args.filename, 'r') as f:
	for line in f:
		analyse = []
		tokens = tokenise(line.strip())
		for tok in tokens:
			tok = tok.lower()
			nb_tok += 1
			
			if tok in punct:
				analyse.append(tok + '[PUNCT]')
			elif isNumber(tok):
				analyse.append(tok + '[NUM.Card]')
			else:
				# Already evaluated
				if tok in forms.keys():
					analyse.append(forms[tok])
				else:
					# Run Quechua analyser
					tok_analyse = runFoma("qwh.foma", tok)
					tok_analyse = list(set(tok_analyse))
					
					# Run guesser
					if tok_analyse[0] == "+?" and not args.no_guesser:
						tok_analyse = runFoma("guess.foma", tok)
						if tok_analyse[0] == "+?":
							tok_analyse = [tok + '[UNK]']
					
					analyse.append(tok_analyse)
					forms[tok] = tok_analyse

		output.write(str(analyse) + '\n')
output.close()

print("{} tokens and {} types parsed.".format(nb_tok, len(forms)))
