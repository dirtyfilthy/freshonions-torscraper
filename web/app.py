from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import url_for
from flask import redirect
from flask import send_from_directory
from flask import session
from flask import g
import urlparse
from pony.orm import *
from datetime import *
from tor_db import *
from tor_elasticsearch import *
from tor_cache import *
import helpers
import re
import os
import bitcoin
import version
import email_util
import banned
import tor_text
import portscanner
import urllib
import random
import sys
import uuid
import detect_language
app = Flask(__name__)
app.jinja_env.globals.update(Domain=Domain)
app.jinja_env.globals.update(WebComponent=WebComponent)
app.jinja_env.globals.update(NEVER=NEVER)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(count=count)
app.jinja_env.globals.update(select=select)
app.jinja_env.globals.update(isinstance=isinstance)
app.jinja_env.globals.update(dict=dict)
app.jinja_env.globals.update(int=int)
app.jinja_env.globals.update(str=str)
app.jinja_env.globals.update(unicode=unicode)
app.jinja_env.globals.update(break_long_words=tor_text.break_long_words)
app.jinja_env.globals.update(is_elasticsearch_enabled=is_elasticsearch_enabled)
app.jinja_env.globals.update(is_cached=is_cached)

app.secret_key = os.environ['FLASK_SECRET'].decode("string-escape")
BLACKLIST_AGENT = []
#BLACKLIST_AGENT = [ 'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0']
#BLACKLIST_AGENT = [ 'python-requests/2.18.1', 
#					'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0',
#					'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
#					'Go-http-client/1.1',
#					'Scrapy/1.3.3 (+http://scrapy.org)',
#					'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/42.2']


HOUR_SEC = 60 * 60
HALF_AN_HOUR_SEC = HOUR_SEC / 2


@app.before_request
def setup_session():

    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=365*30)
    if not 'uuid' in session:
    	session['uuid'] = str(uuid.uuid4())
    	g.uuid_is_fresh = True
    else:
    	g.uuid_is_fresh = False
    now = datetime.now()
    
    referrer  = request.headers.get('Referer', '')
    path      = request.path
    full_path = request.full_path
    agent     = request.headers.get('User-Agent', '')

    if agent in BLACKLIST_AGENT or len(agent) < 15:
        g.request_log_id = 0
        return render_template('error.html',code=200,message="Layer 8 error. If you want my data, DON'T SCRAPE (too much cpu load), contact me and I will give it to you"), 200

    with db_session:
    	req_log   = RequestLog( uuid=session['uuid'], 
    							uuid_is_fresh=g.uuid_is_fresh, 
    							created_at=now, 
    							agent=agent,
    							referrer=referrer,
    							path=path,
    							full_path=full_path)
    	flush()
    	g.request_log_id = req_log.id


   

@app.context_processor
def inject_elasticsearch():
	return dict(elasticsearch_enabled=is_elasticsearch_enabled())

@app.context_processor
def inject_random_integer():
	return dict(random_integer=random.randint(0, sys.maxint-1))

@app.context_processor
def inject_uuid():
	return dict(uuid=session['uuid'], uuid_is_fresh=g.uuid_is_fresh)


@app.context_processor
def inject_revision():
	return dict(revision=version.revision())

@app.context_processor
@db_session
def inject_counts():
	event_horizon = datetime.now() - timedelta(days=1)
	domain_count = cache_memoize("count.domain",    lambda: count(d for d in Domain if d.is_up == True and d.is_crap == False and d.is_subdomain == False  and d.is_banned == False))
	day_count    = cache_memoize("count.new_today", lambda: count(d for d in Domain if d.is_up == True and d.is_crap == False and d.is_subdomain == False  and d.is_banned == False and d.created_at > event_horizon))
	return dict(day_count=day_count, domain_count=domain_count)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',code=404,message="Page not found."), 404

@cached(timeout=HOUR_SEC, render_layout=False)
@app.route('/json/all')
@db_session
def json():
	now = datetime.now()
	event_horizon = now - timedelta(days=30)
	domains = Domain.select(lambda p: p.last_alive > event_horizon and p.is_banned==False).order_by(desc(Domain.created_at))
	return jsonify(Domain.to_dict_list(domains))

@app.route("/")
@cached(timeout=300)
@db_session
def index():
	now = datetime.now()
	context = helpers.build_search_context()

	r = helpers.maybe_search_redirect(context["search"])
	if r:
		return r
	request_log = RequestLog.get(id=g.request_log_id)

	r, n_results = helpers.maybe_domain_search(context)
	if r:
		sl = SearchLog(request_log=request_log, context=context, is_json=False, created_at=now, results=n_results)
		return r

	r, n_results = helpers.render_elasticsearch(context)
	sl = SearchLog(request_log=request_log, context=context, is_json=False, created_at=now, results=n_results)
	return r

@app.route("/json")
@cached(timeout=300, render_layout=False)
@db_session
def index_json():
	
	context = helpers.build_search_context()

	request_log = RequestLog.get(id=g.request_log_id)

	r, n_results = helpers.maybe_domain_search(context, json=True)

	if r:
		sl = SearchLog(request_log=request_log, context=context, is_json=True, created_at=now, results=n_results)
		return r

	r, n_results = helpers.render_elasticsearch(context, json=True)
	sl = SearchLog(request_log=request_log, context=context, is_json=True, created_at=now, results=n_results)

	return r

@app.route('/blank/<random>.css')
def blank(random):
	return render_template("blank.html")
	
@app.route('/src')
def src():
	version_string = version.version()
	source_name="torscraper-%s.tar.gz" % version_string
	source_link="/static/%s" % source_name
	return render_template('src.html', source_name=source_name, source_link=source_link)


@app.route('/onion/<onion>')
@cached(timeout=None)
@db_session
def onion_info(onion):
	links_to = []
	links_from = []
	domain = select(d for d in Domain if d.host==onion).first()
	if domain and domain.is_banned:
		domain = None
	
	if domain:
		fp_count = 0
		paths = domain.interesting_paths()
		emails = domain.emails()
		bitcoin_addresses = domain.bitcoin_addresses()
		if domain.language != '':
			language = detect_language.code_to_lang(domain.language)
		else:
			language = None
		if domain.ssh_fingerprint:
			fp_count = len(domain.ssh_fingerprint.domains)
		links_to   = domain.links_to()
		links_from = domain.links_from()
		return render_template('onion_info.html', domain=domain, language=language, scanner=portscanner, OpenPort=OpenPort, paths=paths, emails=emails, bitcoin_addresses=bitcoin_addresses, links_to=links_to, links_from = links_from, fp_count=fp_count)
	else:
		return render_template('error.html', code=404, message="Onion not found."), 404


@app.route('/onion/<onion>/json')
@cached(timeout=None, render_layout=False)
@db_session
def onion_info_json(onion):
	links_to = []
	links_from = []
	domain = select(d for d in Domain if d.host==onion).first()
	return jsonify(domain.to_dict(full=True))

@app.route('/clones/<onion>')
@cached(timeout=HOUR_SEC)
@db_session
def clones_list(onion):
	domain = select(d for d in Domain if d.host==onion).first()
	if not domain:
		return render_template('error.html', code=404, message="Onion not found."), 404
	domains = Domain.hide_banned(domain.clones())
	return render_template('clones_list.html', onion=onion, domains=domains) 

@app.route('/clones/<onion>/json')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def clones_list_json(onion):
	domain = select(d for d in Domain if d.host==onion).first()
	if not domain:
		return render_template('error.html', code=404, message="Onion not found."), 404
	domains = Domain.hide_banned(domain.clones())
	return jsonify(Domain.to_dict_list(domains))

@app.route('/whatweb/<name>')
@cached(timeout=HOUR_SEC)
@db_session
def whatweb_list(name):
	version = request.args.get("version")
	account = request.args.get("account")
	string  = request.args.get("string")
	domains = WebComponent.find_domains(name, version=version, account=account, string=string)
	return render_template('whatweb_list.html', domains=domains, name=name, version=version, account=account, string=string) 

@app.route('/whatweb/<name>/json')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def whatweb_list_json(name):
	version = request.args.get("version")
	account = request.args.get("account")
	string  = request.args.get("string")
	domains = WebComponent.find_domains(name, version=version, account=account, string=string)
	return jsonify(Domain.to_dict_list(domains))

@app.route('/languages')
@db_session
def languages():
	lang = request.args.get("lang")
	if lang:
		return redirect(url_for("language_list",code=lang), code=302)

	languages = select(d.language for d in Domain if d.language!='')
	options = []
	for code in languages:
		if code == "en" or code == '':
			continue
		lang_count = count(Domain.by_language(code))
		lang_name  = detect_language.code_to_lang(code)
		lang_disp  = "%s (%d)" % (lang_name, lang_count)
		option = []
		option.append(code)
		option.append(lang_disp)
		options.append(option)
	options.sort(key=lambda o: o[1])
	options = [["", "Choose language..."]] + options
	return render_template('languages.html', options=options) 

@app.route('/language/<code>')
@cached(timeout=HOUR_SEC)
@db_session
def language_list(code):
	domains = Domain.hide_banned(Domain.by_language(code))
	if len(domains) != 0:
		language = detect_language.code_to_lang(code)
		return render_template('language_list.html', domains=domains, code=code, language=language)
	else:
		return render_template('error.html', code=404, message="No domains with language '%s'." % code), 404

@app.route('/language/<code>/json')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def language_list_json(code):
	domains = Domain.hide_banned(Domain.by_language(code))
	if len(domains) != 0:
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="No domains with language '%s'." % code), 404

@app.route('/path/<path:path>')
@cached(timeout=HOUR_SEC)
@db_session
def path_list(path):
	path = "/" + path
	domains = Domain.hide_banned(Domain.domains_for_path(path))
	if len(domains) != 0:
		return render_template('path_list.html', domains=domains, path=path)
	else:
		return render_template('error.html', code=404, message="Path '%s' not found." % path), 404

@app.route('/path_json/<path:path>')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def path_list_json(path):
	path = "/" + path
	domains = Domain.hide_banned(Domain.domains_for_path(path))
	if len(domains) != 0:
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Path '%s' not found." % path), 404


@app.route('/ssh/<id>')
@cached(timeout=HOUR_SEC)
@db_session
def ssh_list(id):
	fp = SSHFingerprint.get(id=id)
	if fp:
		domains = Domain.hide_banned(fp.domains)
		fingerprint = fp.fingerprint
		return render_template('ssh_list.html', id=id, domains=domains, fingerprint=fingerprint)
	else:
		return render_template('error.html', code=404, message="Fingerprint not found."), 404

@app.route('/ssh/<id>/json')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def ssh_list_json(id):
	fp = SSHFingerprint.get(id=id)
	if fp:
		domains = Domain.hide_banned(fp.domains)
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Fingerprint not found."), 404

@app.route('/email/<addr>')
@cached(timeout=HOUR_SEC)
@db_session
def email_list(addr):
	email = Email.get(address=addr)
	if email:
		domains = Domain.hide_banned(email.domains())
		return render_template('email_list.html', domains=domains, email=addr)
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/email/<addr>/json')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def email_list_json(addr):
	email = Email.get(address=addr)
	if email:
		domains = Domain.hide_banned(email.domains())
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/port/<ports>')
@cached(timeout=HOUR_SEC)
@db_session
def port_list(ports):
	port_list_s = ports.split(",")
	port_list = []
	for p in port_list_s:
		try:
			port_list.append(int(p.strip()))
		except ValueError:
			pass
	port_list_str = ", ".join(map(lambda p: "%s:%s" % (str(p), portscanner.get_service_name(p)), port_list))
	domains = select(d for d in Domain for op in OpenPort if op.domain==d and op.port in port_list and not d.is_banned)
	if len(domains) > 0:
		return render_template('port_list.html', domains=domains, ports=ports, port_list_str = port_list_str)
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/port/<ports>/json')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def port_list_json(ports):
	port_list_s = ports.split(",")
	port_list = []
	for p in port_list_s:
		try:
			port_list.append(int(p.strip()))
		except ValueError:
			pass
	domains = select(d for d in Domain for op in OpenPort if op.domain==d and op.port in port_list and not d.is_banned)
	if len(domains) > 0:
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/bitcoin/<addr>')
@cached(timeout=HOUR_SEC)
@db_session
def bitcoin_list(addr):
	btc_addr = BitcoinAddress.get(address=addr)
	if btc_addr:
		domains = Domain.hide_banned(btc_addr.domains())
		return render_template('bitcoin_list.html', domains=domains, addr=addr)
	else:
		return render_template('error.html', code=404, message="Email not found."), 404


@app.route('/bitcoin/<addr>/json')
@cached(timeout=HOUR_SEC, render_layout=False)
@db_session
def bitcoin_list_json(addr):
	btc_addr = BitcoinAddress.get(address=addr)
	if btc_addr:
		domains = Domain.hide_banned(btc_addr.domains())
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/faq')
def faq():
	return render_template('faq.html')


@app.route('/bot/<kind>')
@db_session
def bot(kind):
	now = datetime.now()
	hb = HeadlessBot.get(uuid=session["uuid"])
	if hb is None:
		hb=HeadlessBot(uuid=session["uuid"], kind=kind, created_at=now)
		commit()
	return render_template('error.html', code=404, message="Printer on fire."), 404

@app.route('/stats')
@cached(timeout=600)
@db_session
def stats():
	statz = DailyStat.get_stats()
	search_terms = select(sl.searchterms for sl in SearchLog if sl.has_searchterms == True 
						and sl.is_firstpage == True and sl.results > 0).order_by(raw_sql('sl.created_at DESC')).limit(10)

	searches = map(lambda st: select(sl for sl in SearchLog if sl.has_searchterms == True 
						and sl.is_firstpage == True and sl.results > 0 and 
						sl.searchterms == st).order_by(desc(SearchLog.created_at)).first(), search_terms)

	irc_servers = count(d for d in Domain for op in OpenPort if op.domain==d and op.port == 6667)
	banned = count(d for d in Domain if d.is_banned == True)
	return render_template('stats.html', stats=statz, searches=searches, irc_servers=irc_servers, banned=banned)



if __name__ == "__main__":
	app.run(host="0.0.0.0")