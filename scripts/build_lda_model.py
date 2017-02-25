#!/usr/bin/python
from gensim import corpora, models
import gensim
import gensim.models.ldamodel
import autocategorize.corpus as corpus
import sys
import logging

CHUNKSIZE = 20000

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

if len(sys.argv) < 3:
	print "Usage %s NTOPICS NPASSES" % sys.argv[0]
	sys.exit(1)

TOPICS = int(sys.argv[1])
PASSES = int(sys.argv[2])

print "Loading dictionary..."
dictionary = corpora.Dictionary.load(corpus.DICTIONARY_PATH)
print "Loading corpus..."
corp = corpus.load_corpus()
print "Building LDA model..."
ldamodel = gensim.models.ldamodel.LdaModel(corp, num_topics=TOPICS, id2word = dictionary, passes=PASSES, chunksize=CHUNKSIZE)
print "Saving model"
ldamodel.save(corpus.MODEL_PATH)
print(ldamodel.print_topics(num_topics=TOPICS, num_words=10))
print "Done!"
sys.exit(0)