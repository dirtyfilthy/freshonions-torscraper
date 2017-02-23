import os
from tor_db import *
from stop_words import get_stop_words
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models


EXTRA_STOP_WORDS = [
			"http",
			"nbsp",
			"color",
			"border",
			"background"
	]

DICTIONARY_PATH = os.environ['BASEDIR']+"/var/lib/dictionary"
CORPUS_PATH = os.environ['BASEDIR']+"/var/lib/corpus.mm"
MODEL_PATH = os.environ['BASEDIR']+"/var/lib/lda.model"

class FrontpageDocuments(object):

	@db_session
	def __iter__(self):
		domains = select(d for d in Domain if d.is_up == True and d.is_fake == False and d.is_subdomain == False)
		for domain in domains:
			page = select(p for p in Page if p.domain == domain and p.is_frontpage == True).first()
			commit()
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
	dictionary.filter_extremes(no_below=5, no_above=0.3)
	return dictionary

def build_corpus(tokenized_documents, dictionary):
	for text in  tokenized_documents:
		yield dictionary.doc2bow(text)

def save_corpus(corpus):
	corpora.MmCorpus.serialize(CORPUS_PATH, corpus)

def load_corpus():
	corpus = corpora.MmCorpus(CORPUS_PATH)
	return corpus



