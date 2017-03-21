from pony.orm import *
from tor_db.db import db
import tor_db.models
class WebComponent(db.Entity):
    _table_   = "web_component"
    name      = Required(str, 128)
    version   = Optional(str, 128)
    account   = Optional(str, 128)
    string    = Optional(str, 512)
    domains   = Set("Domain", table="web_component_link", reverse="web_components", column="domain")

    @classmethod
    @db_session
    def find_or_create(klass, name, version=None, account=None, string=None):
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


    @classmethod
    @db_session
    def find_domains(klass, name, version=None, account=None, string=None):
    	query = select(d for d in tor_db.models.domain.Domain for wc in d.web_components if wc.name == name)
    	if version:
    		query = query.filter("wc.version == version")
    	if account:
    		query = query.filter("wc.account == account")
    	if string:
    		query = query.filter("wc.string == string")
    	return query

        