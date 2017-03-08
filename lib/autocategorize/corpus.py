from tor_db import *
from stop_words import get_stop_words
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import tor_paths
import datetime

DICTIONARY_PATH = tor_paths.VARDIR + "/lib/autocategorize.dict"
CORPUS_PATH     = tor_paths.VARDIR + "/lib/autocategorize.mm"
MODEL_PATH      = tor_paths.VARDIR + "/lib/autocategorize.model"

EXTRA_STOP_WORDS = [
			"http"
	]

class FrontpageDocuments(object):

	def __iter__(self):
		event_horizon = datetime.now() - timedelta(hours=48)
		domains = select(d for d in Domain if d.is_up == True and d.last_alive > event_horizon 
                         and (d.clone_group is None or d.created_at == 
                         min(d2.created_at for d2 in Domain if d2.clone_group==d.clone_group)))
		for domain in domains:
			page = domain.frontpage()
			if not page:
				continue
			body_stripped = page.get_body_stripped()
			if not body_stripped:
				continue
			yield body_stripped


def tokenize(doc):
	raw = doc.lower()
	tokenizer = RegexpTokenizer(r'\w+')
	return tokenizer.tokenize(raw)

def remove_stopwords(tokenized_doc):
	stop_words = get_stop_words("en") + EXTRA_STOP_WORDS
	return [i for i in tokenized_doc if not i in stop_words]

def stem(tokenized_doc):
	p_stemmer = PorterStemmer()
	return [p_stemmer.stem(i) for i in tokenized_doc]

def clean_tokenized_document(tokenized_doc):
	cleaned = remove_stopwords(tokenized_doc)
	cleaned = stem(cleaned)
	return cleaned

def tokenize_documents(documents):
	for doc in documents:
		tokenized = tokenize(doc)
		cleaned   = clean_tokenized_document(tokenized)
		yield cleaned

def build_dictionary(tokenized_documents):
	dictionary = corpora.Dictionary(tokenized_documents)
	dictionary.filter_extremes(no_below=5, no_above=1.01)
	return dictionary

def build_corpus(tokenized_documents, dictionary):
	for text in  tokenized_documents:
		yield dictionary.doc2bow(text)

def save_corpus(corpus):
	corpora.MmCorpus.serialize(corpus, CORPUS_PATH)

def load_corpus():
	return corpora.MmCorpus.load(CORPUS_PATH)



