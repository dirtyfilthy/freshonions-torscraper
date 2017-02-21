import os
import re
INTERESTING_PATHS_FILENAME = os.environ['ETCDIR'] + "/interesting_paths"
PATHS = [line.strip() for line in open(INTERESTING_PATHS_FILENAME)]

def is_dir(path):
	if re.match(r'.*/$', path):
		return True

def construct_urls(domain):
	first_part = domain.index_url()[:-1]
	return map(lambda p: first_part + p, PATHS)