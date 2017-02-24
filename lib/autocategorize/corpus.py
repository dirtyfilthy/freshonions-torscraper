import os
from tor_db import *
from stop_words import get_stop_words
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import re


EXTRA_STOP_WORDS = [
			"http",
			"nbsp",
			"color",
			"border",
			"background",
			"top",
			"left",
			"margin",
			"return",
			"function",
			"var",
			"ul",
			"li",
			"width",
			"child",
			"hover",
			"import",
			"btn"
			"self",
			"content",
			"height",
			"name",
			"css",
			"length",
			"style",
			"document",
			"getelementbyid",
			"null",
			"type",
			"document",
			"window",
			"font",
			"div",
			"bottom",
			"right",
			"text",
			"url",
			"class",
			"true",
			"false",
			"param",
			"btn",
			"span",
			"padding",
			"html",
			"script",
			"align",
			"size",
			"navbar",
			"panel",
			"input",
			"object",
			"new",
			"rgba",
			"block",
			"webkit",
			"display",
			"none",
			"glyphicon",
			"moz",
			"solid",
			"box",
			"javascript",
			"menu",
			"group",
			"error",
			"linear",
			"gradient",
			"dropdown",
			"item",
			"list",
			"push",
			"result",
			"call",
			"browser",
			"year",
			"january",
			"febuary",
			"march",
			"april",
			"may",
			"june",
			"july",
			"august",
			"september",
			"october",
			"november",
			"december",
			"jan",
			"feb",
			"mar",
			"may",
			"jun",
			"jul",
			"aug",
			"oct",
			"sep",
			"sept",
			"nov",
			"dec",
			"ago",
			"typeof",
			"amp",
			"img",
			"float",
			"black"
	]

POST_STEM_STOP_WORDS = [
			"posit",
			"self",
			"col",
			"moz",
			"prototyp",
			"tabl",
			"imag",
			"param",
			"els",
			"radiu",
			"none",
			"disabl",
			"new",
			"use",
			"will",
			"can",
			"say",
			"nav",
			"first",
			"last",
			"menu",
			"box",
			"shadow",
			"import",
			"form",
			"fff",
			"biginteg",
			"anim",
			"keyfram",
			"hour",
			"day",
			"year",
			"week",
			"serif",
			"san",
			"bold",
			"inset",
			"quot",
			"time",
			"focu",
			"code",
			"http",
			"activ",
			"transit",
			"bttn",
			"buttn",
			"weight",
			"center",
			"decor",
			"auto",
			"data",
			"get",
			"set",
			"filltext",
			"com",
			"org",
			"net",
			"transpar",
			"bodi",
			"tbodi",
			"overflow",
			"absolut",
			"button",
			"visibl",
			"floor",
			"famili",
			"middot",
			"element",
			"updat",
			"ffffff",
			"png",
			"target",
			"hidden",
			"transform",
			"line",
			"inlin",
			"addeventlisten",
			"createel",
			"target",
			"rel",
			"default",
			"min",
			"max",
			"everythingexceptflag",
			"tri",
			"catch",
			"flag",
			"todataurl",
			"textarea",
			"fileref",
			"border",
			"titl",
			"jpg",
			"document",
			"woocommerc",
			"vertic"

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

def _remove_stopwords(tokenized_doc, stop_words):
	return [i for i in tokenized_doc if not i in stop_words]

def remove_stopwords(tokenized_doc):
	stop_words = get_stop_words("en") + EXTRA_STOP_WORDS
	return _remove_stopwords(tokenized_doc, stop_words)

def post_stem_remove_stopwords(tokenized_doc):
	return _remove_stopwords(tokenized_doc, POST_STEM_STOP_WORDS)
	

def remove_numbers(tokenized_doc):
	return [i for i in tokenized_doc if not re.match(r".*\d", i)]

def remove_small(tokenized_doc):
	return [i for i in tokenized_doc if not len(i)<3]

def stem(tokenized_doc):
	p_stemmer = PorterStemmer()
	return [p_stemmer.stem(i) for i in tokenized_doc]

def clean_tokenized_document(tokenized_doc):
	cleaned = remove_stopwords(tokenized_doc)
	cleaned = remove_numbers(cleaned)
	cleaned = stem(cleaned)
	cleaned = remove_small(cleaned)
	cleaned = post_stem_remove_stopwords(cleaned)
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
	for text in  tokenized_documents:
		yield dictionary.doc2bow(text)

def save_corpus(corpus):
	corpora.MmCorpus.serialize(CORPUS_PATH, corpus)

def load_corpus():
	corpus = corpora.MmCorpus(CORPUS_PATH)
	return corpus



