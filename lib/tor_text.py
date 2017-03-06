import re
def break_long_words(text):
	return re.sub("([^ <>\\t\\n\\r\\f\\v]{35,70})","\\1 ", text)

def strip_html(text):
	return re.sub('<[^<]+?>', '', text)