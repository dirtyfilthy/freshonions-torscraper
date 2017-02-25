from pony.orm import *
from tor_db.db import db
class CloneGroup(db.Entity):
    _table_   = "clone_group"
    domains    = Set('Domain')
    new_clone_group_domains = Set('Domain', reverse="new_clone_group")