#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 
import urllib2
from urllib2 import URLError
import random
import string
import socket
import ssl

@db_session
def get_domains():
	domains = select(d for d in Domain if d.is_up == True and d.useful_404_scanned_at == NEVER)
	return domains


@db_session 
def scan_404():
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	domains = get_domains()
	print("processing %d domains" % count(domains))
	i = 0
	for d in domains:
		i += 1
		r = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(12))
		url = d.index_url() + r
		code = 0
		try:
			res = urllib2.urlopen(url, None, 60, context=ctx)
			code = int(res.getcode())		
		except urllib2.HTTPError, e:
			code = int(e.code)		
		except (URLError, socket.timeout, ssl.CertificateError) as e:
			print("#%d failed (%s)" % (i, url))
			continue
		
		if code in [502, 503]:
			print("#%d failed (%s)" % (i, url))
			continue
		print("#%d tested %s and got %d" % (i, url, code))
		if code == 404:
			d.useful_404 = True
		else:
			d.useful_404 = False	
		d.useful_404_scanned_at = datetime.now()
		commit()

scan_404()
sys.exit(0)