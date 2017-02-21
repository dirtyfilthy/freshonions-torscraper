from pony.orm import *
from tor_db.db import db
from tor_db.constants import *
from datetime import *
import urlparse
class Page(db.Entity):
    url          = Required(str, unique=True)
    title        = Optional(str)
    code         = Required(int)
    is_frontpage = Required(bool, default=False)
    domain       = Required('Domain')
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
            domain = Domain.find_stub_by_url(url)
            p = klass(url=url, domain=domain, code=666, created_at=now, visited_at=NEVER, title='')

        return p

    @classmethod
    def is_frontpage_url(klass, url):
        parsed_url = urlparse.urlparse(url)
        path  = '/' if parsed_url.path=='' else parsed_url.path
        if path == '/':
            return True

        return False


    def got_server_response(self):
        responded = [200, 401, 403, 500, 302, 304]
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