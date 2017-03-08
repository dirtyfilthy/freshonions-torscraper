#!/usr/bin/python
import autocategorize.corpus as corpus
import sys
print "Loading dictionary..."
dictionary = corpora.Dictionary.load(corpus.DICTIONARY_PATH)
print "Building corpus..."
tokenized = corpus.tokenize_documents(corpus.FrontpageDocuments())
corpus_lib = corpus.build_corpus(tokenized, dictionary)
corpus.save_corpus(corpus_lib)
print "Done!"
sys.exit(0)