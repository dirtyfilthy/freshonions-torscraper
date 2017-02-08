#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 

@db_session
def create_fingerprint():
	host   = sys.argv[1]
	fprint = sys.argv[2]
	domain = Domain.get(host=host)
	if not domain:
		sys.exit(1)

	ssh_fprint = SSHFingerprint.get(fingerprint=fprint)
	if not ssh_fprint:
		ssh_fprint = SSHFingerprint(fingerprint=fprint)

	domain.ssh_fingerprint = ssh_fprint
	return None

create_fingerprint()
sys.exit(0)