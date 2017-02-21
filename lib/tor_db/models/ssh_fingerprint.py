from pony.orm import *
from tor_db.db import db
class SSHFingerprint(db.Entity):
    _table_ = "ssh_fingerprint"
    fingerprint = Required(str, 450, unique=True)
    domains = Set('Domain', reverse="ssh_fingerprint")