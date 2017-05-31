from pony.orm import *
from tor_db.db import db
from tor_db.constants import *
from tor_db.models.domain import *
import tor_db.models.domain
import elasticsearch.exceptions
from tor_elasticsearch import *
from datetime import *
import urlparse
class Page(db.Entity):
    url          = Required(str, unique=True)
    title        = Optional(str)
    code         = Required(int)
    is_frontpage = Required(bool, default=False)
    domain       = Required('Domain')
    size         = Required(int, default=0)
    path         = Optional(str, 1024)
    created_at   = Required(datetime)
    visited_at   = Required(datetime)
    links_to     = Set("Page", reverse="links_from", table="page_link", column="link_to");
    links_from   = Set("Page", reverse="links_to",   table="page_link", column="link_from");
    emails       = Set('Email', reverse="pages", column="email", table="email_link")
    bitcoin_addresses = Set('BitcoinAddress', reverse="pages", column="bitcoin_address", table="bitcoin_address_link")

    @classmethod
    @db_session
    def find_stub_by_url(klass, url):
        now = datetime.now()
        p = klass.get(url=url)
        if not p:
            domain = tor_db.models.domain.Domain.find_stub_by_url(url)
            p = klass(url=url, domain=domain, code=666, created_at=now, visited_at=NEVER, title='')

        return p

    @classmethod
    def find_old(klass):
        now = datetime.now()
        event_horizon = now - timedelta(days=30)
        pages = select(p for p in Page if p.visited_at < event_horizon).limit(100)
        return pages


    @classmethod
    @db_session
    def delete_old(klass):
        print "find old"
        i = 1
        pages = Page.find_old()
        while(len(pages) > 0):
            for page in pages:
                page.links_from.clear()
                page.links_to.clear()
                page.delete()
                
                
                if (i % 50) == 0:
                    print i
                i += 1
            
            commit()
            pages = Page.find_old()

    @classmethod
    def is_frontpage_url(klass, url):
        parsed_url = urlparse.urlparse(url)
        path  = '/' if parsed_url.path=='' else parsed_url.path
        if path == '/':
            return True

        return False

    @classmethod
    def path_from_url(klass, url):
        parsed_url = urlparse.urlparse(url)
        path  = '/' if parsed_url.path=='' else parsed_url.path
        return path



    def before_delete(self):
        try:
            ep = PageDocType.get(id = self.url, parent = self.domain.host)
            ep.delete()
        except elasticsearch.exceptions.NotFoundError:
            pass

    def before_insert(self):
        self.path  = Page.path_from_url(self.url)

    def before_update(self):
        self.path  = Page.path_from_url(self.url)

    def get_body_stripped(self):
        res = elasticsearch_retrieve_page_by_id(self.id)
        if res:
            return elasticsearch_retrieve_page_by_id(self.id)["body_stripped"]
        else:
            return None

    def get_body(self):
        res = elasticsearch_retrieve_page_by_id(self.id)
        if res:
            return elasticsearch_retrieve_page_by_id(self.id)["body"]
        else:
            return None


    def got_server_response(self):
        responded = [200, 401, 403, 500, 302, 304, 206]
        return (self.code in responded)

    @classmethod
    def is_frontpage_request(klass, request):
        if klass.is_frontpage_url(request.url):
            return True
        if request.meta.get('redirect_urls'):
            for url in request.meta.get('redirect_urls'):
                if klass.is_frontpage_url(url):
                    return True

        return False