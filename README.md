# qishwar

Repository of resources for Ancash Quechua.

## Morphological analyser
The morphological analyser is based on the [Foma](https://fomafst.github.io/) library. It consists of two modules: an analysis model for terms whose root is in Quechua, and a guesser that can be called if this analysis fails.

### Foma installation (Debian/Ubuntu)
```sudo apt install foma```

### Use the analyser
From CLI (without guesser): 
```
echo "akray" | flookup -x qwh.foma
```

With Python script: 
```
python run_morpho_analyser.py filename.txt -o output.txt
```


## Corpora

### Dictionaries
- Gary J. PARKER, _Diccionario polilectal del quechua de Ancash_, 1975
- MINEDU, _Yachakuqkunapa Shimi Qullqa, Anqash Qichwa Shimichaw_, 2005
- G. SWISSHELM. _Un diccionario del quechua de Huaraz : quechua-castellano, castellano-quechua_, 1972 


### Narratives
- Santiago PANTOJA RAMOS, José RIPKENS, Germán SWISSHELM, _Cuentos y relatos en el quechua de Ancash_, 2 vol., Estudios Culturales Benedictinos, 1974
- Macedonio VILLAFÁN BRONCANO. _Apu Kolki Hirka_. 1997
