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

    @classmethod
    @db_session
    def unique_visitors_since(klass, event_horizon):
    	return count(log.uuid for log in klass if log.created_at > event_horizon and log.uuid_is_fresh == False)
