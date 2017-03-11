import os
from tor_db import *
from stop_words import get_stop_words
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from datetime import *
import re
import tor_paths
from datetime import *

DICTIONARY_PATH = tor_paths.VARDIR + "/lib/autocategorize.dict"
CORPUS_PATH     = tor_paths.VARDIR + "/lib/autocategorize.mm"
MODEL_PATH      = tor_paths.VARDIR + "/lib/autocategorize.model"

POST_STEM_STOP_WORDS = []


EXTRA_STOP_WORDS = [
			"nbsp",
			"gt",
			"lt",
			"amp",
			"quot"
	]

class FrontpageDocuments(object):

	@db_session
	def __iter__(self):
		event_horizon = datetime.now() - timedelta(hours=48)
		domain_ids = select(d.id for d in Domain if d.is_up == True and d.last_alive > event_horizon 
                         and (d.clone_group is None or d.created_at == 
                         min(d2.created_at for d2 in Domain if d2.clone_group==d.clone_group)))
		domain_ids = list(domain_ids)

		for d_id in domain_ids:
			domain = Domain.get(id = d_id)
			page = domain.frontpage()
			if not page:
				continue
			body_stripped = page.get_body_stripped()
			commit()
			if not body_stripped:
				continue
			yield body_stripped
		commit()


def tokenize(doc):
	raw = doc.lower()
	tokenizer = RegexpTokenizer(r'\w+')
	return tokenizer.tokenize(raw)

def remove_stopwords(tokenized_doc, stop_words):
	return [i for i in tokenized_doc if not i in stop_words]

def remove_numbers(tokenized_doc):
	return [i for i in tokenized_doc if not re.match(r"^\d+$", i)]

def stem(tokenized_doc):
	p_stemmer = PorterStemmer()
	return [p_stemmer.stem(i) for i in tokenized_doc]

def clean_tokenized_document(tokenized_doc):
	cleaned = remove_stopwords(tokenized_doc, get_stop_words("en") + EXTRA_STOP_WORDS)
	cleaned = stem(cleaned)
	cleaned = remove_stopwords(cleaned, POST_STEM_STOP_WORDS)
	cleaned = remove_numbers(cleaned)
	return cleaned

def tokenize_documents(documents):
	for doc in documents:
		tokenized = tokenize(doc)
		cleaned   = clean_tokenized_document(tokenized)
		yield cleaned

def build_dictionary(tokenized_documents):
	dictionary = corpora.Dictionary(tokenized_documents)
	dictionary.filter_extremes(no_below=5, no_above=0.5)
	return dictionary

def build_corpus(tokenized_documents, dictionary):
	plain = []
	i = 0
	for text in  tokenized_documents:
		plain.append(dictionary.doc2bow(text))
		i += 1
		if (i % 10) == 0:
			print("processed %d documents" % i)
		
	return plain

def save_corpus(corpus):
	corpora.MmCorpus.serialize(CORPUS_PATH, corpus)

def load_corpus():
	return corpora.MmCorpus(CORPUS_PATH)

def save_corpus(corpus):
	corpora.MmCorpus.serialize(CORPUS_PATH, corpus)

def load_corpus():
	corpus = corpora.MmCorpus(CORPUS_PATH)
	return corpus



