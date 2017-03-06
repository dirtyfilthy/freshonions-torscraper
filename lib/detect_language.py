from langid.langid import LanguageIdentifier, model
from tor_db import *


def classify(text):
	identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
	lang, prob = identifier.classify(text)
	if prob > 0.75:
		return lang
	return None

def detect_domain(domain):
	fp = domain.firstpage()
	if fp is None:
		return None
	body = fp.get_body_stripped()
	lang = classify(body)
	if lang is None:
		lang = ''
	domain.language = lang
	domain.commit()


