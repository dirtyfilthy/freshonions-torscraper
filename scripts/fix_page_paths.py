#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import urlparse
import portscanner
import sys 

@db_session
def get_pages(page, limit):
	pages = select(p for p in Page if p.path=='').page(page, limit)
	return pages

@db_session
def fix_paths():
	limit = 1000
	n_results = limit
	page = 0
	while n_results == limit:
		page += 1
		query = get_pages(page, limit)
		n_results = count(query)

		for p in query:
			p.path = Page.path_from_url(p.url)
			print("Set path %s for %s" % (p.path, p.url))

		commit()


fix_paths()
sys.exit(0)