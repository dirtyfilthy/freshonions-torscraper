from pony.orm import *
from tor_db.db import db
from tor_db.constants import *
import tor_db.models.email
import tor_db.models.bitcoin_address
from datetime import *
import bitcoin
from tor_elasticsearch import *
import pretty
import banned
import os
import re
import dateutil.parser
import urlparse

class Domain(db.Entity):
    host         = Required(str)
    port         = Required(int)
    pages        = Set('Page')
    ssl          = Required(bool)
    is_up        = Required(bool)
    title        = Optional(str)
    server       = Optional(str)
    powered_by   = Optional(str)
    is_crap      = Required(bool, default=False)
    is_fake      = Required(bool, default=False)
    is_genuine   = Required(bool, default=False)
    is_subdomain = Required(bool, default=False)
    is_banned    = Required(bool, default=False)
    created_at   = Required(datetime)
    visited_at   = Required(datetime)
    last_alive   = Required(datetime)
    open_ports   = Set('OpenPort')
    next_scheduled_check = Required(datetime)
    dead_in_a_row   = Required(int, default=0)
    ssh_fingerprint = Optional('SSHFingerprint')
    portscanned_at  = Required(datetime, default=NEVER)
    path_scanned_at = Required(datetime, default=NEVER)


    def status(self):
        now = datetime.now()
        event_horizon = now - timedelta(hours=4)

        if self.is_up:
            return 'alive'
        elif self.last_alive > event_horizon:
            return 'maybe'
        else:
            return 'dead'

    @db_session
    def get_open_ports(self):
        op = map(lambda p: p.port, list(self.open_ports))
        web_ports = select(d.port for d in Domain if d.host == self.host and d.is_up == True)
        return list(set(op + list(web_ports)))


    def before_insert(self):
        if (self.title.find("Site Hosted by Freedom Hosting II") != -1 or
            self.title.find("Freedom Hosting II - hacked") != -1):
            self.is_crap = True
        else:
            self.is_crap = False


        if not self.is_genuine and len(self.title) > 8 and not self.title in ["Entry Point", "Login"]:
            genuine_exists = select(d.is_genuine for d in Domain if d.is_genuine == True and self.title == d.title).first()
            if genuine_exists:
                self.is_fake = True

        if self.host.count(".") > 1:
            self.is_subdomain = True

        if banned.contains_banned(self.title):
            self.is_banned = True

        if is_elasticsearch_enabled():
            dom = DomainDocType.from_obj(self)
            dom.save()

        


    def before_update(self):
        if (self.title.find("Site Hosted by Freedom Hosting II") != -1 or
            self.title.find("Freedom Hosting II - hacked") != -1):
            self.is_crap = True
        else:
            self.is_crap = False

        if not self.is_genuine and len(self.title) > 8 and not self.title in ["Entry Point", "Login"]: 
            genuine_exists = select(d.is_genuine for d in Domain if d.is_genuine == True and self.title == d.title).first()
            if genuine_exists:
                self.is_fake = True

        if self.is_up:
            self.dead_in_a_row = 0
            self.next_scheduled_check = datetime.now() + timedelta(hours=1)

        if banned.contains_banned(self.title):
            self.is_banned = True

        if is_elasticsearch_enabled():
            dom = DomainDocType.from_obj(self)
            dom.save()


 

    @db_session
    def to_dict(self, full=False):
        SITE_DOMAIN = os.environ['SITE_DOMAIN']
        d = dict()
        d['url']        = self.index_url()
        d['title']      = self.title
        d['is_up']      = self.is_up
        d['created_at'] = self.created_at
        d['visited_at'] = self.visited_at
        d['last_seen']  = self.last_alive
        d['is_genuine'] = self.is_genuine
        d['is_fake']    = self.is_fake
        d['server']     = self.server
        d['hostname']   = self.host
        d['powered_by'] = self.powered_by
        d['portscanned_at'] = self.portscanned_at

        if full == False:
            d['more_info'] = "http://%s/onion/%s/json" % (SITE_DOMAIN, self.host)

        if self.ssh_fingerprint:
            d['ssh_fingerprint']  = self.ssh_fingerprint.fingerprint
        else:
            d['ssh_fingerprint']  = None

        if full:
            links_to   = self.links_to()
            links_from = self.links_from()
            emails     = self.emails()
            btc_addr   = self.bitcoin_addresses()
            d['links_to']   = []
            d['links_from'] = [] 
            d['emails']     = []
            d['bitcoin_addresses'] = []
            d['open_ports'] = self.get_open_ports()
            for link_to in links_to:
                d['links_to'].append(link_to.index_url())
            for link_from in links_from:
                d['links_from'].append(link_from.index_url())
            for email in emails:
                d["emails"].append(email.address)
            for addr in btc_addr:
                d["bitcoin_addresses"].append(addr.address)

        return d

    @classmethod
    def to_dict_list(klass, ary, full=False):
        ret = []
        for d in ary:
            ret.append(d.to_dict(full))

        return ret


    @classmethod
    def time_ago(klass, time):
        if isinstance(time, basestring):
            time = dateutil.parser.parse(time)
        if time==NEVER:
            return "Never"
        else:
            p=pretty.date(time)
            p=p.replace(" ago","")
            p=p.replace("years", "yr")
            p=p.replace("year", "yr")
            p=p.replace("minutes", "min")
            p=p.replace("seconds", "sec")
            p=p.replace("second", "sec")
            p=p.replace("minute", "min")
            p=p.replace("hours", "hr")
            p=p.replace("hour", "hr")
            p=p.replace("days", "d")
            p=p.replace("day", "d")
            p=p.replace("weeks", "wk")
            p=p.replace("week", "wk")
            p=p.replace("months", "mth") 
            p=p.replace("month", "mth")
            return p 

    def index_url(self):
        schema = "https" if self.ssl else  "http"
        if self.port!=80 and self.port!=443:
            return "%s://%s:%d/" % (schema, self.host, self.port)
        else:
            return "%s://%s/" % (schema, self.host)

    @db_session
    def fingerprint(self):
        return self.ssh_fingerprint.fingerprint if self.ssh_fingerprint else None

    @db_session
    def links_to(self):
        return select(d for d in Domain for p in d.pages for link_to in p.links_to if link_to.domain==self)

    @db_session
    def links_from(self):
        return select(d for d in Domain for p in d.pages for link_from in p.links_from if link_from.domain==self)

    @db_session
    def emails(self):
        return select(e for e in tor_db.models.email.Email for p in e.pages if p.domain == self)

    @db_session
    def bitcoin_addresses(self):
        return select(b for b in tor_db.models.bitcoin_address.BitcoinAddress for p in b.pages if p.domain == self).limit(100)


    @classmethod
    @db_session
    def make_genuine(klass, host):
        domainz = select(d for d in Domain if d.host == host)
        title = ""
        for domain in domainz:
            domain.is_genuine = True
            domain.is_fake = False
            title = domain.title

        if domain.title.strip()!="" and not domain.title in ["Login", "Entry Point"]:
            fakes = select(d for d in Domain if d.is_genuine == False and d.title == title)
            for fake in fakes:
                fake.is_fake = True
        
        commit()
        return None

    
    @classmethod
    @db_session
    def find_stub(klass, host, port, ssl):
        domain = klass.get(host=host, port=port, ssl=ssl)
        if not domain:
            domain = klass(host=host, port=port, ssl=ssl, is_up=False, title='', created_at=datetime.now(), visited_at=NEVER, last_alive=NEVER)
        return domain


    @classmethod
    def find_by_host(klass, host):
        return klass.find_stub(host, 80, False)

    @classmethod
    @db_session
    def find_by_url(klass, url):
        try:
            parsed_url = urlparse.urlparse(url)
            host  = parsed_url.hostname
            port  = parsed_url.port
            ssl   = parsed_url.scheme=="https://"
            if not port:
                if ssl:
                    port = 443
                else:
                    port = 80
            return klass.get(host=host, port=port, ssl=ssl)
        except:
            return None


    @classmethod
    def find_stub_by_url(klass, url):
        parsed_url = urlparse.urlparse(url)
        host  = parsed_url.hostname
        port  = parsed_url.port
        ssl   = parsed_url.scheme=="https://"
        if not port:
            if ssl:
                port = 443
            else:
                port = 80
        return klass.find_stub(host, port, ssl)

    @classmethod
    def is_onion_url(klass, url):
        try:
            parsed_url = urlparse.urlparse(url)
            host  = parsed_url.hostname
            if re.match("[a-zA-Z0-9.]+\.onion$", host):
                return True
            else:
                return False
        except:
            return False
