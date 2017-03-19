from pony.orm import *
from tor_db.db import db
class WebComponent(db.Entity):
    _table_   = "web_component"
    name      = Required(str, 128)
    version   = Optional(str, 128)
    account   = Optional(str, 128)
    string    = Optional(str, 512)
    domains   = Set("Domain", reverse="web_component", table="web_component_link", column="domain")

    @classmethod
    @db_session
    def find_or_create(name, version=None, account=None, string=None):
    	if version is None:
    		version = ""
    	if account is None:
    		account = ""
    	if string is None:
    		string  = ""
    	wc = WebComponent.get(name=name, version=version, account=account, string=string)
    	if not wc:
    		wc = WebComponent(name=name, version=version, account=account, string=string)
    	return wc
        