from pony.orm import *
from tor_db.db import db
import tor_db.models.domain
class Email(db.Entity):
    address = Required(str, 100, unique=True)
    pages = Set('Page', reverse="emails", column="page", table="email_link")

    def domains(self):
    	return select(d for d in tor_db.models.domain.Domain for p in d.pages for e in p.emails if e == self)