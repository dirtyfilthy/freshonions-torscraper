import os
import re
import tor_paths
INTERESTING_PATHS_FILENAME = tor_paths.ETCDIR + "/interesting_paths"
PATHS = [line.strip() for line in open(INTERESTING_PATHS_FILENAME)]
PATHS_DIR   = []
PATHS_PHP   = []
PATHS_OTH   = []

def is_dir(path):
	if re.match(r'.*/$', path):
		return True
	return False

def is_php(path):
	if re.match(r".*\.php$", path):
		return True
	return False

def construct_urls(domain):
	first_part = domain.index_url()[:-1]
	return map(lambda p: first_part + p, PATHS)

for p in PATHS:
	if is_dir(p):
		PATHS_DIR.append(p)
	elif is_php(p):
		PATHS_PHP.append(p)
	else:
		PATHS_OTH.append(p)