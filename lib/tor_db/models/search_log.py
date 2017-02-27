from pony.orm import *
from tor_db.db import db
from datetime import *
class SearchLog(db.Entity):
    _table_             = "search_log"
    created_at          = Required(datetime)
    request_log         = Required('RequestLog')
    has_searchterms     = Required(bool, default=False)
    searchterms         = Optional(str, 256)
    raw_searchterms     = Optional(str, 256)
    context             = Required(Json)
    is_json             = Required(bool, default=False)
    is_firstpage        = Required(bool, default=False)
    has_raw_searchterms = Required(bool, default=False)
    results             = Required(int)

    def before_insert(self):
    	self.searchterms = self.context['search'].strip()
        self.raw_searchterms = self.context['raw_search'].strip()
    	if self.searchterms != '':
    		self.has_searchterms = True
        if self.raw_searchterms != '':
            self.has_raw_searchterms = True

    	page = self.context.get('page')
    	if not page or int(page) == 1:
    		self.is_firstpage = True
