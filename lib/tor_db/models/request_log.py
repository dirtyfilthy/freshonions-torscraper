from pony.orm import *
from tor_db.db import db
from datetime import *
class RequestLog(db.Entity):
    _table_       = "request_log"
    uuid          = Required(str, 36)
    uuid_is_fresh = Required(bool)
    created_at    = Required(datetime)
    path          = Required(str, 1024)
    full_path     = Required(str, 1024)
    agent         = Optional(str, 256)
    referrer      = Optional(str, 1024)
    search_log    = Optional('SearchLog')
