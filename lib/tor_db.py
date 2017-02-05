import urlparse 
import re
from pony.orm import *
from datetime import *
import pretty
db = Database()
db.bind('mysql', host='groan', user='root', passwd='fuck', db='tor')
NEVER = datetime.fromtimestamp(0)


class Domain(db.Entity):
    host        = Required(str)
    port        = Required(int)
    pages       = Set('Page')
    ssl         = Required(bool)
    is_up       = Required(bool)
    title       = Optional(str)
    is_crap     = Required(bool, default=False)
    is_fake     = Required(bool, default=False)
    is_genuine  = Required(bool, default=False)
    created_at  = Required(datetime)
    visited_at  = Required(datetime)
    last_alive  = Required(datetime)


    def status(self):
        now = datetime.now()
        event_horizon = now - timedelta(hours=4)

        if self.is_up:
            return 'alive'
        elif self.last_alive > event_horizon:
            return 'maybe'
        else:
            return 'dead'


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

    @classmethod
    def time_ago(klass, time):
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
        commit()
        return domain


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
        return find_stub_by_url(klass, host, port, ssl)

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
            
class Page(db.Entity):
    url         = Required(str, unique=True)
    title       = Optional(str)
    code        = Required(int)
    domain      = Required(Domain)
    created_at  = Required(datetime)
    visited_at  = Required(datetime)

db.generate_mapping(create_tables=True)