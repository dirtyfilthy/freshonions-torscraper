from tor_db import *
import urllib2
from bs4 import BeautifulSoup
import sys
import os

@db_session
def add_domains(category, parsed_page):
	div = parsed_page.find(class_="table-responsive")
	#print(parsed_page)
	#print("#### div ####")
	#print(div)
	rows = div.table.tbody.find_all("tr")
	for row in rows:
		# this is totally fucked and makes no sense ???
		td = row.find_all("td")[2]
		s = td.string
		print("")
		
		
		print("Adding domain %s to category %s" % (s, category.name))
		domain = Domain.find_by_url(s)
		if not domain:
			continue
		category.add_confirmed_domain(domain)

def get_pagination_links(category, parsed_page):
	links_bs = parsed_page.find_all("a", class_="pagination-css")
	links = []
	# man beautifulsoup4 is really fucking broken, i should be able to the below but
	# it replaces & with =
	# for link in links_bs:
	#	 l = "http://easyonionsantyma.onion/" + link["href"]
	#	 links.append(l) 

	n = (len(links_bs) / 2) - 3
	print("len %d" % n)
	if n < 1:
		return []
	for i in range(2, n+2):
		links.append("http://easyonionsantyma.onion/dir.php?p=%d&r=category&cat=%s" % (i, category.name))

	return links

@db_session
def copy_category(name):
	category=Category.get(name=name.lower())
	if not category:
		category = Category(name=name.lower(), is_auto=True)
	cat_url = ("http://easyonionsantyma.onion/dir.php?r=category&cat=%s" % name)
	page = urllib2.urlopen(cat_url).read()
	parsed_page = BeautifulSoup(page, "lxml")
	add_domains(category, parsed_page)
	links = get_pagination_links(category, parsed_page)
	for link in links:
		print("Following pagination link %s" % link)
		page = urllib2.urlopen(link).read()

		parsed_page = BeautifulSoup(page, "lxml")
		add_domains(category, parsed_page)


if len(sys.argv) < 2:
	print("Usage: %s category", sys.argv[0])

copy_category(sys.argv[1])






