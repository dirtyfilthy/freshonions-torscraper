from pony.orm import *
from tor_db.db import db
from datetime import *
class HeadlessBot(db.Entity):
	_table_   = "headless_bot"
	uuid       = PrimaryKey(str, 36)
	kind       = Optional(str, 128)
	created_at = Required(datetime)

 