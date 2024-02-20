import sys
import csv
import re
import string
from ast import literal_eval

def toSet(analyser_output):
	elems = re.split('\+|\[', analyser_output)
	#print("To set {}".format(elems))
	analyse = []
	i=1
	while i < len(elems):
		analyse.append((elems[i-1].replace('(guessed)', ''), '[' + elems[i]))
		i += 2
	return analyse

# Renvoie une liste de tuples de la forme (morphème de surface, morphème lemmatisé)
# Paramètres : forme de surface (chaîne de caractères), liste de morphèmes lemmatisés
def matchSurfaceForm(surface_form, morphs_list):
	i=0 # indice du morphème courant
	x=0 # indice de début (segment de la forme de surface courante)
	y=0
	vowel_shortening = ['naA', 'paA', 'raA', 'YkaA', 'kaA', 'llaA', 'yaA', 'maA', 'kachaA', 'tsaA']
	finalI = ['mi', 'shi']
	equivalences = {'rI':['ra'], 'ː':['a', 'i', 'u'], 'ːkuna':['akuna', 'ikuna', 'ukuna'], 'kU':['ka'], 'pu':['pa'], 'qam':['qan'], 'yku':['yka'], 'qarqu':['qarqa'], 'yarqu':['yarqa'], 'rantikU':['rantika']}
	root = ['rikaa', 'mantsakaa', 'chaa', 'wamayaa', 'shaa']
	closedSyl = ['yku', 'ykaa', 'rku', 'rqu', 'rqa', 'pti', 'shqa', 'r', 'yaa']
	
	index_ep = -1
	if 'ni' in surface_form[2:]:
		index_ep = checkEpenthesis(morphs_list)
		print("Épenthèse : {}".format(index_ep))

	liste_correspondances = []

	while i<len(morphs_list):
		if i == index_ep:
			liste_correspondances.append(('ni', 0))
			x += 2
			y += 2

		y += len(morphs_list[i])
		
		if morphs_list[0] in root and morphs_list[1].lower() in closedSyl:
			y -= 1
			liste_correspondances.append((morphs_list[0][:-1], morphs_list[0]))
			x+=len(morphs_list[0])-1
			i+=1
			continue
			
		current_surface_morph = surface_form[x:y]
		current_morph = morphs_list[i]
		
		print(i, current_surface_morph, current_morph)

		if current_morph in vowel_shortening:
			# Cas où le morphème est dans sa forme longue
			if current_surface_morph == current_morph.lower() and morphs_list[i+1] != 'ː':
				liste_correspondances.append((current_surface_morph, current_morph))
				x+=len(current_morph)
				i+=1
				
			else:
				temp_morph = current_morph.replace('A', '')
				temp_morph = temp_morph.lower()
				if current_surface_morph[:-1] == temp_morph or current_surface_morph == temp_morph:
					liste_correspondances.append((current_surface_morph[:-1], current_morph))
					print(liste_correspondances)
					x+=len(current_morph) - 1
					y-=1
					i+=1
				else:
					print("Cas non traité abaissement vocalique")
					exit(1)
		
		# Cas forme de surface = forme lemmatisée
		elif current_surface_morph.lower() == current_morph.lower():
			liste_correspondances.append((current_surface_morph, current_morph))
			x+=len(current_surface_morph)
			i+=1
		
		# Variations de graphie fréquentes	
		elif current_surface_morph.lower().replace('k', 'q') == current_morph.lower() or current_surface_morph.lower().replace('k', 'q') == current_morph.lower():
			liste_correspondances.append((current_surface_morph, current_morph))
			x+=len(current_surface_morph)
			i+=1
	
		
		# Cas particuliers de transformations
		elif current_morph in equivalences:			
			if current_surface_morph in equivalences[current_morph]:
				liste_correspondances.append((current_surface_morph, current_morph))
				x+=len(current_morph)
				i+=1
			else:
				# Homophonie yku et ku après /i/
				if current_morph == 'yku' and morphs_list[i-1][-1] == 'i':
					liste_correspondances.append(('ku', 'yku'))
					y -= 1
					x+=2
					i+=1
				else:
					print("Cas non traité de formes équivalentes")
					exit(1)
		
		# Correspondance m -> mi en fin de mot
		elif i == len(morphs_list) -1 and current_morph in finalI:
			liste_correspondances.append((current_surface_morph, current_morph))
			i+=1
		

			 
		else:
			print("Erreur sur l'élément {} : forme de surface {} / morphème {}".format(surface_form, current_surface_morph, current_morph))
			exit(1)
			
	return liste_correspondances


# Détermine si une épenthèse est nécessaire au vu de la suite de morphèmes
# et renvoie l'indice de sa position dans la liste de morphèmes le cas échéant
def checkEpenthesis(morphs):
	i = 0
	print(morphs)
	for m in morphs[:-1]:
		lastchars = m[-2:]
		nextmorph = morphs[i+1]
		
		if (not m[-1] in "aiuAIU" \
		or lastchars == 'aa' or lastchars == 'ii' or lastchars == 'uu') \
		and (nextmorph[0] == 'n' or nextmorph[0] == 'y' or nextmorph == 'ː'):
			return i+1
			break;
		else:
			i+=1
		
	return -1
	

# Applique la lemmatisation sur un terme et son analyse
# Renvoie la liste des correspondance (morphèmes de surface, lemme)
def lemmatize(surface_form, analyser_output):
	analyse = toSet(analyser_output)
	morphs = [x[0] for x in analyse]
	corresp = matchSurfaceForm(surface_form, morphs)
	return corresp

# Paramètres
param=sys.argv
if len(param) < 2:
	print("File name missing. Input : csv file with col1: qwh sentence | col2: analyser_output\n")
	exit(1)

res = []

with open(param[1], newline='') as f:
  csvreader = csv.reader(f, delimiter='\t')
  for row in csvreader:
	  # Phrase texte brut
	  sentence_raw = row[0]
	  print(sentence_raw)

	  # Analyse gold
	  gold = row[3].strip()
	  gold = gold.replace('][', '.')
	  gold = list(literal_eval(gold))
	  print(gold)
	  
	  # Tokenisation
	  punct = [',', '.', '?', '!', "'", '"', '“', '”', ':','‘','’', ';', '—']
	  sentence = "".join(c for c in sentence_raw if c not in punct)
	  tokens = sentence.split(' ')
	  
	  lemmas = []
	  for tok, analyse in zip(tokens, gold):
	  	lemmas.append(lemmatize(tok, str(analyse[0])))
	  res.append(lemmas)
	  print(res)


with open("session-2/lemmas.txt", 'w') as output:
	output.write("\n".join(str(item) for item in res))
