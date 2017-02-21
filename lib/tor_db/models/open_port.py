from pony.orm import *
from tor_db.db import db
class OpenPort(db.Entity):
    _table_   = "open_port"
    port      = Required(int)
    domain    = Required('Domain') 

    @classmethod
    @db_session
    def count_open(klass, port):
        return count(p for p in OpenPort if p.port==port)