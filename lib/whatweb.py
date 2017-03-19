import tor_paths
import tor_db
from datetime import *
import tempfile
import json
import os
from subprocess import call

WHATWEB_BIN = tor_paths.THIRDPARTY_DIR + "/WhatWeb/whatweb"
IGNORE_PLUGINS = [ "title", "email" ]

def from_html(html):
	with tempfile.NamedTemporaryFile() as input_file:

		input_file.write(html)
		input_file.flush()

		fh, output_path = tempfile.mkstemp()
		fh.close()

		subprocess.call([WHATWEB_BIN, "--log-json", output_path, input_file.name])
		with open(output_path, "r") as fh2:
			json_raw = fh2.read()

		os.unlink(output_path)

		return json.loads(json_raw)[0]

@db_session
def domain(dom):
	
	frontpage = dom.frontpage()
	if frontpage is None:
		return None
	
	html = frontpage.get_body()
	if html is None:
		return None

	return whatweb_from_html(html)


@db_session
def process(dom):
	whatweb_data = domain(dom)
	dom.whatweb_at = datetime.now()
	dom.web_components.clear()
	if whatweb_data is None:
		return None
	for plugin, data in whatweb_data["plugins"].iteritems():
		name = plugin.lower()
		if name in IGNORE_PLUGINS:
			continue
		account = data.get("account")[0] if data.get("account") else None
		version = data.get("version")[0] if data.get("version") else None
		string  = data.get("string")[0]  if data.get("string")  else None
		wc = WebComponent.find_or_create(name, account=account, version=version, string=string)
		dom.web_components.add(wc)

@db_session
def process_all:
	horizon  = datetime.now() - timedelta(weeks=1)
	horizon2 = datetime.now() - timedelta(hours=48)
	domain_ids = list(select(d.id for d in Domain if d.whatweb_at < horizon and d.last_alive > horizon2))
	total = len(domain_ids)
	i=0
	for did in domain_ids:
		i=i+1
		dom = Domain.get(id=did)
		if (i % 50) == 0:
			print("Processing %d / %d" % (i, total))
		process(dom)
		commit()







