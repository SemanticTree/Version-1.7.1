from collections import namedtuple
import spacy
import warnings
import numpy as np


connection = namedtuple('connection', 'node weight')
Index = namedtuple('Index', 'pid, sid, wid')

nlp = spacy.load('en')
# spacy.load('/tmp/en_wiki', vocab=nlp.vocab)  # used for the time being

# spacy.load('en_vectors_web_lg', vocab=nlp.vocab)
warnings.filterwarnings("ignore")

# Global Variables
THRESHOLD = 0.7  # MD-TPM
TREE = None  # Final Tree Object
ROOT = None  # Final root of Tree
DOC = None  # Actual doc object for the function
SENT_RANGE = None
WORD_RANGE = None
SECTION_JOIN_THRESHHOLD = 0.95
NODE_TAGS = ['NOUN', 'ADJ']
PAIR_MAX_CONNECTIONS = 20

def get_freq_sorted_dictionary():
	from collections import defaultdict
	f = open("Corpus Frequency Data/20k.txt","r")
	ranked_words=defaultdict()
	for l1 in f.readlines():
	    ranked_words[l1[0:-1]]=len(ranked_words)+1
	return ranked_words

WORD_RANKING=get_freq_sorted_dictionary()