import os
import re
import tor_paths
BANNED_WORD_FILENAME = tor_paths.ETCDIR + "/banned_words"
BANNED_WORDS = [line.strip() for line in open(BANNED_WORD_FILENAME) if line.strip()!='']
BANNED_WORDS_REGEX_STR = ""
start = True

for word in BANNED_WORDS:
	if not start:
		BANNED_WORDS_REGEX_STR += '|'
	BANNED_WORDS_REGEX_STR += '\\b' + ('%s' % word ) + '\\b'
	start = False

BANNED_WORDS_REGEX = re.compile(BANNED_WORDS_REGEX_STR, re.IGNORECASE)

def contains_banned(text):
	if re.search(BANNED_WORDS_REGEX, text):
		return True
	return False

def delete_banned(text):
	return re.sub(BANNED_WORDS_REGEX, "", text)
