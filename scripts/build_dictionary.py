#!/usr/bin/python
import autocategorize.corpus as corpus
import sys
print "Building dictionary..."
tokenized = corpus.tokenize_documents(corpus.FrontpageDocuments())
dictionary = corpus.build_dictionary(tokenized)
dictionary.save(corpus.DICTIONARY_PATH)
print "Done!"
sys.exit(0)