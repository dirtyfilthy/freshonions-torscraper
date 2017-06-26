import scrapy
import urlparse 
import re
from collections import *
from pony.orm import *
from datetime import *
from tor_db import *
from tor_elasticsearch import *
import json
import random
import tor_text
import string
import random
import timeout_decorator
import bitcoin
import email_util
import interesting_paths
import tor_text

from scrapy.exceptions import IgnoreRequest

def maybe_add_scheme(onion):
    o = onion.strip()
    if not re.match(r"^(http|https)://", o):
        o = ("http://%s/" % o)
    return o

@db_session
def domain_urls_down():
    urls = []
    now = datetime.now()
    event_horizon = now - timedelta(days=30)
    n_items = count(d for d in Domain if d.last_alive > event_horizon and d.is_up == False)
    for domain in Domain.select(lambda d: d.is_up == False and d.last_alive > event_horizon).random(n_items):
        urls.append(domain.index_url())
    return urls

@db_session
def domain_urls_resurrect():
    urls = []
    now = datetime.now()
    event_horizon = now - timedelta(days=30)
    n_items = count(d for d in Domain if d.last_alive < event_horizon and d.is_up == False)
    for domain in Domain.select(lambda d: d.is_up == False and d.last_alive < event_horizon).random(n_items):
        urls.append(domain.index_url())
    return urls

@db_session
def domain_urls():
    urls = []
    for domain in Domain.select():
        urls.append(domain.index_url())
    return urls

@db_session
def domain_urls_recent_no_crap():
    urls = []
    now = datetime.now()
    event_horizon = now - timedelta(days=30)
    n_items = count(d for d in Domain if d.is_up == True and d.is_crap == False)
    for domain in Domain.select(lambda d: d.is_up == True and d.is_crap == False).random(n_items):
        urls.append(domain.index_url())
    return urls

@db_session
def domain_urls_recent():
    urls = []
    now = datetime.now()
    event_horizon = now - timedelta(days=30)
    n_items = count(d for d in Domain if d.last_alive > event_horizon)
    for domain in Domain.select(lambda d: d.last_alive > event_horizon).random(n_items):
        urls.append(domain.index_url())
    return urls

@db_session
def domain_urls_next_scheduled():
    urls = []
    now = datetime.now()

    for domain in Domain.select(lambda d: now > d.next_scheduled_check).order_by(Domain.visited_at):
        urls.append(domain.index_url())
    return urls

@db_session
def domain_urls_next_scheduled_old():
    urls = []
    now = datetime.now()
    event_horizon = now - timedelta(days=30)
    for domain in Domain.select(lambda d: now > d.next_scheduled_check and d.last_alive > event_horizon).order_by(Domain.visited_at):
        urls.append(domain.index_url())
    return urls

class TorSpider(scrapy.Spider):
    name = "tor"
    allowed_domains = ['onion']
    handle_httpstatus_list = [404, 403, 401, 503, 500, 504, 502, 206]
    start_urls = domain_urls_recent_no_crap()
    if len(start_urls) == 0:
        start_urls = [
            'http://gxamjbnu7uknahng.onion/',
            'http://mijpsrtgf54l7um6.onion/',
            'http://dirnxxdraygbifgc.onion/',
            'http://torlinkbgs6aabns.onion/'
        ]

    custom_settings = {
        'DOWNLOAD_MAXSIZE': (1024 * 1024)*2,
        'BIG_DOWNLOAD_MAXSIZE': (1024 * 1024)*4,
        'ALLOW_BIG_DOWNLOAD': [
            'cratedvnn5z57xhl.onion'
        ],
        'INJECT_RANGE_HEADER': True,
        'ROBOTSTXT_OBEY': False,
	    'CONCURRENT_REQUESTS' : 24,
        'CONCURRENT_REQUESTS_PER_DOMAIN' : 6,
        'DEPTH_PRIORITY' : 8,
        'DOWNLOAD_TIMEOUT': 90,
        'RETRY_TIMES': 1,
        'MAX_PAGES_PER_DOMAIN' : 1000,
        'HTTPERROR_ALLOWED_CODES': handle_httpstatus_list,
        'RETRY_HTTP_CODES': [],
        'DOWNLOADER_MIDDLEWARES' : {
            'torscraper.middlewares.FilterDomainByPageLimitMiddleware' : 551,
            'torscraper.middlewares.FilterTooManySubdomainsMiddleware' : 550,
            'torscraper.middlewares.FilterDeadDomainMiddleware' : 556,
            'torscraper.middlewares.AllowBigDownloadMiddleware' : 557,
            'torscraper.middlewares.FilterNotScheduledMiddleware' : 558,
         },
         'SPIDER_MIDDLEWARES' : {
            'torscraper.middlewares.InjectRangeHeaderMiddleware' : 543,
         },
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    spider_exclude = [
        'blockchainbdgpzk.onion',
        'ypqmhx5z3q5o6beg.onion'
    ]

    

    def __init__(self, *args, **kwargs):
        super(TorSpider, self).__init__(*args, **kwargs)
        if hasattr(self, "passed_url"):
            self.start_urls = [self.passed_url]
        elif hasattr(self, "load_links") and self.load_links == "downonly":
            self.start_urls = domain_urls_down()
        elif hasattr(self, "load_links") and self.load_links == "resurrect":
            self.start_urls = domain_urls_resurrect()
        elif hasattr(self, "load_links"):
            self.start_urls = [maybe_add_scheme(line) for line in open(self.load_links)]
        elif hasattr(self, "test") and self.test == "yes":
            if hasattr(self, "alive") and self.alive == "yes":
                self.start_urls = domain_urls_next_scheduled_old()
            else:
                self.start_urls = domain_urls_next_scheduled()
            self.custom_settings['CONCURRENT_REQUESTS'] = 40
        else:
            self.start_urls = domain_urls_recent_no_crap()




    @db_session
    def update_page_info(self, url, title, code, is_frontpage=False, size=0):
        
        if not Domain.is_onion_url(url):
            return False
        
        if title == "ERROR: The requested URL could not be retrieved":
            return False

        failed_codes = [666, 503, 504, 502]
        responded_codes = [200, 206,403, 500, 401, 301, 302, 304, 400]
        if (hasattr(self, "only_success") and self.only_success == "yes" and 
            code not in responded_codes):
            return False

        if not title:
            title = ''
        parsed_url = urlparse.urlparse(url)
        host  = parsed_url.hostname
        if host == "zlal32teyptf4tvi.onion":
            return False

        port  = parsed_url.port
        ssl   = parsed_url.scheme=="https://"
        path  = '/' if parsed_url.path=='' else parsed_url.path
        is_up = not code in failed_codes
        if not port:
            if ssl:
                port = 443
            else:
                port = 80
            
        now = datetime.now()
      
        domain = Domain.get(host=host, port=port, ssl=ssl)
        is_crap = False
        if not domain:
            if is_up:
                last_alive = now
            else:
                last_alive = NEVER
                title=''
            domain=Domain(host=host, port=port, ssl=ssl, is_up=is_up, last_alive=last_alive, 
                created_at=now, next_scheduled_check=(now + timedelta(hours=1)), visited_at=now, title=title)
            self.log("created domain %s" % host)
        else:
            domain.is_up      = is_up
            domain.visited_at = now
            if is_up:

                if domain.last_alive == NEVER:
                    domain.created_at = now

                domain.last_alive = now

                if is_frontpage:
                    if not (domain.title != '' and title == ''):
                        domain.title = title

        page = Page.get(url=url)
        if not page:
            page = Page(url=url, title=title, code=code, created_at=now, visited_at=now, domain=domain, is_frontpage=is_frontpage, size=size)
        else:
            if is_up:
                page.title = title
            page.code = code
            page.visited_at = now
            page.size = size
            if not page.is_frontpage and is_frontpage:
                page.is_frontpage = is_frontpage
       
        return page

    
    @timeout_decorator.timeout(5)
    @db_session
    def extract_other(self, page, body):
        self.log("extract_other")
        page.emails.clear()
        self.log("find_emails")
        for addr in re.findall(email_util.REGEX, body):
            addr = addr.lower()
            self.log("found email %s" % addr)
            email = Email.get(address=addr)
            if not email:
                email = Email(address=addr)
            page.emails.add(email)

        page.bitcoin_addresses.clear()
        self.log("find_bitcoin")
        for addr in re.findall(bitcoin.REGEX, body):
            self.log("testing address %s" % addr)
            if not bitcoin.is_valid(addr):
                continue
            bitcoin_addr = BitcoinAddress.get(address=addr)
            if not bitcoin_addr:
                bitcoin_addr = BitcoinAddress(address=addr)
            page.bitcoin_addresses.add(bitcoin_addr)


    @db_session
    def description_json(self, response):
        domain = Domain.find_by_url(response.url)
        if not domain or response.status in [502, 503]:
            return None
        if response.status in [200, 206]:
            domain.description_json = json.loads(response.body)
        else:
            domain.description_json = None



    @db_session
    def useful_404_detection(self, response):
        domain = Domain.find_by_url(response.url)
        is_php = re.match(r".*\.php$", response.url)
        is_dir = re.match(r".*/$", response.url)
        if not domain or response.status in [502, 503]:
            return None
        if response.status == 404:
            if is_php:
                domain.useful_404_php = True
            elif is_dir:
                domain.useful_404_dir = True
            else:
                domain.useful_404     = True
        else:
            if is_php:
                domain.useful_404_php = False
            elif is_dir:
                domain.useful_404_dir = False
            else:
                domain.useful_404     = False
    
        domain.useful_404_scanned_at = datetime.now()
        return None

    @db_session
    def parse(self, response, recent_alive_check=False):
        MAX_PARSE_SIZE_KB = 1000
        title = ''
        try:
            title = response.css('title::text').extract_first()
        except AttributeError:
            pass
        parsed_url = urlparse.urlparse(response.url)
        host  = parsed_url.hostname
        if host != "zlal32teyptf4tvi.onion":  
            self.log('Got %s (%s)' % (response.url, title))
            is_frontpage = Page.is_frontpage_request(response.request)
            size = len(response.body)
            
            page = self.update_page_info(response.url, title, response.status, is_frontpage, size)
            if not page:
                return

            # extra headers

            got_server_response = page.got_server_response()
            if got_server_response and response.headers.get("Server"):
                page.domain.server = tor_text.utf8_conv(response.headers.get("Server"))
            if got_server_response and response.headers.get("X-Powered-By"):
                page.domain.powered_by = tor_text.utf8_conv(response.headers.get("X-Powered-By"))
            if got_server_response and response.headers.get("Powered-By"):
                page.domain.powered_by = tor_text.utf8_conv(response.headers.get("Powered-By"))
            domain = page.domain
            
                
            if domain.is_up:
                domain.dead_in_a_row = 0
                domain.next_scheduled_check = datetime.now() + timedelta(minutes = random.randint(60, 180)) 
            else:
                yield_later = None
                # check newly dead domains immediately
                if domain.dead_in_a_row == 0 and not recent_alive_check:
                    self.log('checking the freshly dead (%s) for movement' % domain.host)
                    r = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(7,12)))
                    test_url = domain.index_url() + r
                    yield_later = scrapy.Request(test_url, callback=lambda r: self.parse(r, recent_alive_check=True))
                if not recent_alive_check:
                    domain.dead_in_a_row += 1
                    if domain.dead_in_a_row > 16:
                        domain.dead_in_a_row = 16
                    domain.next_scheduled_check = (datetime.now() + 
                        timedelta(minutes = random.randint(60, 180) * (1.5 ** domain.dead_in_a_row)))

                commit()
                if yield_later:
                    yield yield_later

            is_text = False
            content_type = response.headers.get("Content-Type") 
            if got_server_response and content_type and re.match('^text/', content_type.strip()):
                is_text = True

            # elasticsearch

            if is_elasticsearch_enabled() and is_text:
                self.log('Inserting %s page into elasticsearch' % response.url)
                pg = PageDocType.from_obj(page, response.body)
                pg.save()

            commit()

            # add some randomness to the check

            path_event_horizon = datetime.now() - timedelta(days=14+random.randint(0, 14))

            # interesting paths

            if domain.is_up and domain.path_scanned_at < path_event_horizon:
                domain.path_scanned_at = datetime.now()
                commit()
                for url in interesting_paths.construct_urls(domain):
                    yield scrapy.Request(url, callback=self.parse)

            # /description.json

            if domain.is_up and domain.description_json_at < path_event_horizon:
                domain.description_json_at = datetime.now()
                commit()
                yield scrapy.Request(domain.construct_url("/description.json"), callback=self.description_json)

            # language detection

            if domain.is_up and is_frontpage and (response.status == 200 or response.status == 206):
                domain.detect_language(tor_text.strip_html(response.body))
                commit()

            # 404 detections

            if domain.is_up and is_frontpage and domain.useful_404_scanned_at < (datetime.now() - timedelta(weeks=2)):
                
                # standard

                r = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(7,12)))
                url = domain.index_url() + r
                yield scrapy.Request(url, callback=self.useful_404_detection)

                # php

                r = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(7,12)))
                url = domain.index_url() + r +".php"
                yield scrapy.Request(url, callback=self.useful_404_detection)
               
                # dir

                r = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(7,12)))
                url = domain.index_url() + r +"/"
                yield scrapy.Request(url, callback=self.useful_404_detection)
            
            link_to_list = []
            self.log("Finding links...")

            if (not hasattr(self, "test") or self.test != "yes") and not host in TorSpider.spider_exclude:
                for url in response.xpath('//a/@href').extract():
                    fullurl = response.urljoin(url)
                    yield scrapy.Request(fullurl, callback=self.parse)
                    if got_server_response and Domain.is_onion_url(fullurl):
                        try:
                            parsed_link = urlparse.urlparse(fullurl)
                        except:
                            continue
                        link_host = parsed_link.hostname
                        if host != link_host:
                            link_to_list.append(fullurl)

                self.log("link_to_list %s" % link_to_list)
                    
                if page.got_server_response():
                    small_body = response.body[:(1024*MAX_PARSE_SIZE_KB)]
                    page.links_to.clear()
                    for url in link_to_list:
                        link_to = Page.find_stub_by_url(url)
                        page.links_to.add(link_to)

                    try:
                        self.extract_other(page, small_body)
                    except timeout_decorator.TimeoutError:
                        pass

                    commit()                        


    def process_exception(self, response, exception, spider):
        self.update_page_info(response.url, None, 666);

