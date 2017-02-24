#!/usr/bin/python
from gensim import corpora, models
import autocategorize.corpus as corpus
import sys
print "Loading dictionary..."
dictionary = corpora.Dictionary.load(corpus.DICTIONARY_PATH)
print "Tokenizing documents..."
tokenized = corpus.tokenize_documents(corpus.FrontpageDocuments())
print "Building corpus..."
c = corpus.build_corpus(tokenized, dictionary)
corpus.save_corpus(c)
print "Done!"
sys.exit(0)