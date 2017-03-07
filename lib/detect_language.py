# -- coding: utf-8 --
# encoding=utf8
from langdetect import detect_langs
from tor_db import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import pycountry

def classify(text, debug = False):
	# identifier.set_languages(DETECT_LANGUAGES)
	try:
		lang1 = detect_langs(text)[0]
	except UnicodeDecodeError:
		lang1 = detect_langs(text.decode("utf-8"))[0]
	prob = lang1.prob
	lang = lang1.lang

	if debug:
		return (lang, prob)

	if prob > 0.90:
		return lang

	return None

def code_to_lang(code):
	l = pycountry.languages.get(alpha_2=code)
	if not l:
		return None
	return l.name




