from pony.orm import *
from tor_db.db import db
class CloneGroup(db.Entity):
    _table_   = "clone_group"
    domains    = Set('Domain')
    new_clone_group_domains = Set('Domain', reverse="new_clone_group")

    @classmethod
    @db_session
    def empty_groups(klass):
    	return left_join(g for g in klass for d in g.domains if d is None)

    @classmethod
    @db_session
    def has_genuine(klass):
    	return left_join(g for g in klass for d in g.domains if d is not None and d.is_genuine == True)

    @classmethod
    @db_session
    def update_fakes(klass):
    	for group in klass.has_genuine():
    		for domain in group.domains:
    			if not (domain.manual_genuine or domain.is_genuine or domain.is_fake):
    				domain.is_fake = True
    				print("Setting %s to fake" % domain.host)
    		commit()


    @classmethod
    @db_session
    def delete_empty_groups(klass):
    	empty = klass.empty_groups()
    	n     = count(empty)
    	i=0
    	for group in klass.empty_groups():
    		i += 1
    		group.delete()
    		if i % 10:
    			print("deleted %d / %d" % (i, n))