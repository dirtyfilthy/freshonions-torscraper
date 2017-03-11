from pony.orm import *
from tor_db.db import db
from datetime import *
import tor_db.models.request_log
import tor_db.models.domain
class DailyStat(db.Entity):
    _table_           = "daily_stat"
    created_at        = Required(datetime)
    unique_visitors   = Required(int)
    total_onions      = Required(int)
    total_onions_all  = Required(int)
    new_onions        = Required(int)
    new_onions_all    = Required(int)
    total_clones      = Required(int)
    banned            = Required(int)
    banned_up_last_24 = Required(int)
    up_right_now      = Required(int)
    up_right_now_all  = Required(int)

    @classmethod
    @db_session
    def get_stats(klass):
    	now = datetime.now()
    	event_horizon = now - timedelta(hours=24)
    	r = dict()
    	r['unique_visitors']   = tor_db.models.request_log.RequestLog.unique_visitors_since(event_horizon)
    	r['total_onions_all']  = count(d for d in tor_db.models.domain.Domain if d.last_alive > event_horizon)
    	r['up_right_now_all']  = count(d for d in tor_db.models.domain.Domain if d.last_alive > event_horizon and d.is_up == True)
    	r['new_onions_all']    = count(d for d in tor_db.models.domain.Domain if d.last_alive > event_horizon and d.created_at > event_horizon)
    	r['new_onions']		   = count(d for d in tor_db.models.domain.Domain if d.last_alive > event_horizon and d.created_at > event_horizon and d.is_subdomain == False and d.is_crap == False and d.is_banned == False) 
    	r['total_onions']      = count(d for d in tor_db.models.domain.Domain if d.last_alive > event_horizon and d.is_subdomain == False and d.is_crap == False and d.is_banned == False)
    	r['up_right_now']      = count(d for d in tor_db.models.domain.Domain if d.last_alive > event_horizon and d.is_subdomain == False and d.is_crap == False and d.is_banned == False and d.is_up == True)
    	r['banned']            = count(d for d in tor_db.models.domain.Domain if d.is_banned == True)
    	r['banned_up_last_24'] = count(d for d in tor_db.models.domain.Domain if d.is_banned == True and d.last_alive > event_horizon)
    	r['total_clones']      = count(d for d in tor_db.models.domain.Domain if d.last_alive > event_horizon and d.clone_group != None)
    	clone_groups     = count(d.clone_group for d in tor_db.models.domain.Domain if d.last_alive > event_horizon and d.clone_group != None)
    	r['total_clones'] -= clone_groups
    	return r



    @classmethod
    @db_session
    def new_day(klass):
    	now = datetime.now()
    	stats = klass.get_stats()    	
    	new_day = klass( created_at        = now, 
    					 unique_visitors   = stats['unique_visitors'], 
    					 total_onions      = stats['total_onions'], 
    					 total_onions_all  = stats['total_onions_all'], 
    					 new_onions        = stats['new_onions'],
    					 new_onions_all    = stats['new_onions_all'],
    					 up_right_now      = stats['up_right_now'],
    					 up_right_now_all  = stats['up_right_now_all'],
    					 banned            = stats['banned'],
    					 banned_up_last_24 = stats['banned_up_last_24'],
    					 total_clones     = stats['total_clones'] )