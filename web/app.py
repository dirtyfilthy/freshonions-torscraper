from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import url_for
from flask import redirect
from flask import send_from_directory
import urlparse
from pony.orm import *
from datetime import *
from tor_db import *
from tor_elasticsearch import *
import helpers
import re
import os
import bitcoin
import email_util
import banned
import tor_text
import portscanner
import urllib
app = Flask(__name__)
app.jinja_env.globals.update(Domain=Domain)
app.jinja_env.globals.update(NEVER=NEVER)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(select=select)
app.jinja_env.globals.update(int=int)
app.jinja_env.globals.update(break_long_words=tor_text.break_long_words)
app.jinja_env.globals.update(is_elasticsearch_enabled=is_elasticsearch_enabled)

@app.context_processor
def inject_elasticsearch():
	return dict(elasticsearch_enabled=is_elasticsearch_enabled())


@app.context_processor
@db_session
def inject_counts():
	event_horizon = datetime.now() - timedelta(days=1)
	domain_count = count(d for d in Domain if d.is_up == True and d.is_crap == False and d.is_subdomain == False  and d.is_banned == False)
	day_count    = count(d for d in Domain if d.is_up == True and d.is_crap == False and d.is_subdomain == False  and d.is_banned == False and d.created_at > event_horizon)
	return dict(day_count=day_count, domain_count=domain_count)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',code=404,message="Page not found."), 404

@app.route('/json/all')
@db_session
def json():
	now = datetime.now()
	event_horizon = now - timedelta(days=30)
	domains = Domain.select(lambda p: p.last_alive > event_horizon and p.is_banned==False).order_by(desc(Domain.created_at))
	return jsonify(Domain.to_dict_list(domains))

@app.route("/")
@db_session
def index():

	context = helpers.build_search_context()

	r = helpers.maybe_search_redirect(context["search"])
	if r:
		return r

	r = helpers.maybe_domain_search(context)
	if r:
		return r

	return helpers.render_elasticsearch(context)

@app.route("/json")
@db_session
def index_json():
	
	context = helpers.build_search_context()

	r = helpers.maybe_domain_search(context, json=True)
	if r:
		return r

	return helpers.render_elasticsearch(context, json=True)

	
@app.route('/src')
def src():
	current = os.path.dirname(os.path.realpath(__file__))
	version_file = current+"/../etc/version_string"
	with open(version_file,'r') as f:
		version_string = f.read().strip()

	source_name="torscraper-%s.tar.gz" % version_string
	source_link="/static/%s" % source_name
	return render_template('src.html', source_name=source_name, source_link=source_link)


@app.route('/onion/<onion>')
@db_session
def onion_info(onion):
	links_to = []
	links_from = []
	domain = select(d for d in Domain if d.host==onion).first()
	fp_count = 0
	paths = domain.interesting_paths()
	emails = domain.emails()
	bitcoin_addresses = domain.bitcoin_addresses()
	if domain.ssh_fingerprint:
		fp_count = len(domain.ssh_fingerprint.domains)
	if domain:
		links_to   = domain.links_to()
		links_from = domain.links_from()
		return render_template('onion_info.html', domain=domain, scanner=portscanner, OpenPort=OpenPort, paths=paths, emails=emails, bitcoin_addresses=bitcoin_addresses, links_to=links_to, links_from = links_from, fp_count=fp_count)
	else:
		return render_template('error.html', code=404, message="Onion not found."), 404


@app.route('/onion/<onion>/json')
@db_session
def onion_info_json(onion):
	links_to = []
	links_from = []
	domain = select(d for d in Domain if d.host==onion).first()
	return jsonify(domain.to_dict(full=True))

@app.route('/clones/<onion>')
@db_session
def clones_list(onion):
	domain = select(d for d in Domain if d.host==onion).first()
	if not domain:
		return render_template('error.html', code=404, message="Onion not found."), 404
	domains = domain.clones()
	return render_template('clones_list.html', onion=onion, domains=domains) 

@app.route('/clones/<onion>/json')
@db_session
def clones_list_json(onion):
	domain = select(d for d in Domain if d.host==onion).first()
	if not domain:
		return render_template('error.html', code=404, message="Onion not found."), 404
	domains = domain.clones()
	return jsonify(Domain.to_dict_list(domains))



@app.route('/path/<path:path>')
@db_session
def path_list(path):
	path = "/" + path
	domains = Domain.domains_for_path(path)
	if count(domains) != 0:
		return render_template('path_list.html', domains=domains, path=path)
	else:
		return render_template('error.html', code=404, message="Path '%s' not found." % path), 404

@app.route('/path_json/<path:path>')
@db_session
def path_list_json(path):
	path = "/" + path
	domains = Domain.domains_for_path(path)
	if count(domains) != 0:
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Path '%s' not found." % path), 404


@app.route('/ssh/<id>')
@db_session
def ssh_list(id):
	fp = SSHFingerprint.get(id=id)
	if fp:
		domains = fp.domains
		fingerprint = fp.fingerprint
		return render_template('ssh_list.html', id=id, domains=domains, fingerprint=fingerprint)
	else:
		return render_template('error.html', code=404, message="Fingerprint not found."), 404

@app.route('/ssh/<id>/json')
@db_session
def ssh_list_json(id):
	fp = SSHFingerprint.get(id=id)
	if fp:
		domains = fp.domains
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Fingerprint not found."), 404

@app.route('/email/<addr>')
@db_session
def email_list(addr):
	email = Email.get(address=addr)
	if email:
		domains = email.domains()
		return render_template('email_list.html', domains=domains, email=addr)
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/email/<addr>/json')
@db_session
def email_list_json(addr):
	email = Email.get(address=addr)
	if email:
		domains = email.domains()
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/port/<ports>')
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
	domains = select(d for d in Domain for op in OpenPort if op.domain==d and op.port in port_list)
	if len(domains) > 0:
		return render_template('port_list.html', domains=domains, ports=ports, port_list_str = port_list_str)
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/port/<ports>/json')
@db_session
def port_list_json(ports):
	port_list_s = ports.split(",")
	port_list = []
	for p in port_list_s:
		try:
			port_list.append(int(p.strip()))
		except ValueError:
			pass
	domains = select(d for d in Domain for op in OpenPort if op.domain==d and op.port in port_list)
	if len(domains) > 0:
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/bitcoin/<addr>')
@db_session
def bitcoin_list(addr):
	btc_addr = BitcoinAddress.get(address=addr)
	if btc_addr:
		domains = btc_addr.domains()
		return render_template('bitcoin_list.html', domains=domains, addr=addr)
	else:
		return render_template('error.html', code=404, message="Email not found."), 404


@app.route('/bitcoin/<addr>/json')
@db_session
def bitcoin_list_json(addr):
	btc_addr = BitcoinAddress.get(address=addr)
	if btc_addr:
		domains = btc_addr.domains()
		return jsonify(Domain.to_dict_list(domains))
	else:
		return render_template('error.html', code=404, message="Email not found."), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/faq')
def faq():
	return render_template('faq.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0")