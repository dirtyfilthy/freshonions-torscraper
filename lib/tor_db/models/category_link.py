from pony.orm import *
from tor_db.db import db
from datetime import *
class CategoryLink(db.Entity):
	__table__     = "category_link"
	domain        = Required('Domain')
	category      = Required('Category')
	is_valid      = Required(bool, default=True)
	is_confirmed  = Required(bool, default=False)
	created_at    = Required(datetime, default=lambda: datetime.now())
