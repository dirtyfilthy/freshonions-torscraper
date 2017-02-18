import os
import re
BANNED_WORD_FILENAME = os.environ['ETCDIR'] + "/banned_words"
BANNED_WORDS = [line.rstrip('\n') for line in open(BANNED_WORD_FILENAME)]
BANNED_WORDS_REGEX_STR = ""
start = True

for word in BANNED_WORDS:
	if not start:
		BANNED_WORDS_REGEX_STR += '|'
	BANNED_WORDS_REGEX_STR += ("\b%s\b" % word )
	start = False

BANNED_WORDS_REGEX = re.compile(BANNED_WORDS_REGEX_STR, re.IGNORECASE)

def contains_banned(text)
	if re.search(BANNED_WORDS_REGEX, text):
		return True
	return False

def delete_banned(text)
	return re.sub(BANNED_WORDS, "", text)
