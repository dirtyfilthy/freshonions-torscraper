from pony.orm import *
from tor_db.db import db
from datetime import *
import tor_db
class Category(db.Entity):
	name           = Required(str, 64)
	is_auto        = Required(bool, default=True)
	created_at     = Required(datetime, default=lambda: datetime.now())
	category_links = Set('CategoryLink')

	@db_session
	def add_confirmed_domain(self, domain):
		cl = select(cl for cl in tor_db.models.category_link.CategoryLink if cl.category==self and cl.domain==domain).first()
		if not cl:
			cl = self.category_links.create(domain=domain, is_confirmed=True, is_valid=True)
		else:
			cl.is_confirmed = True
			cl.is_valid = True

