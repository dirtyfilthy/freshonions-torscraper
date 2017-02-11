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
import re
import os
import bitcoin
import email_util
app = Flask(__name__)
app.jinja_env.globals.update(Domain=Domain)
app.jinja_env.globals.update(NEVER=NEVER)
app.jinja_env.globals.update(len=len)
@app.context_processor
@db_session
def inject_counts():
	event_horizon = datetime.now() - timedelta(days=1)
	domain_count = count(d for d in Domain if d.is_up == True and d.is_crap == False and d.is_subdomain == False)
	day_count    = count(d for d in Domain if d.is_up == True and d.is_crap == False and d.is_subdomain == False and d.created_at > event_horizon)
	return dict(day_count=day_count, domain_count=domain_count)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',code=404,message="Page not found."), 404


@app.route("/")
@db_session
def index():
	now = datetime.now()
	query = select(d for d in Domain)
	is_up = request.args.get("is_up")
	if is_up:
		query = query.filter("d.is_up == 1")
	rep = request.args.get("rep")
	if not rep:
		rep = "n/a"
	if rep == "genuine":
		query = query.filter("d.is_genuine == 1")
	if rep == "fake":
		query = query.filter("d.is_fake == 1")

	show_subdomains = request.args.get("show_subdomains")
	if not show_subdomains:
		query = query.filter("d.is_subdomain == 0")

	show_fh_default = request.args.get("show_fh_default")
	if not show_fh_default:
		query = query.filter("d.is_crap == 0")

	search = request.args.get("search")
	if not search:
		search=""
	search = search.strip()
	if search != "":
		if re.match('.*\.onion$', search):
			return redirect(url_for("onion_info",onion=search), code=302)
		elif re.match(email_util.REGEX_ALL, search):
			return redirect(url_for("email_list",addr=search), code=302)
		elif bitcoin.is_valid(search):
			return redirect(url_for("bitcoin_list",addr=search), code=302)
		else:
			query = query.filter("search in d.title")

	never_seen = request.args.get("never_seen")
	if not never_seen:
		query = query.filter("d.last_alive != NEVER")

	query = query.order_by(desc(Domain.created_at))

	more = request.args.get("more")

	if not more:
		query = query.limit(1000)

	n_results = len(query)

	return render_template('index.html', domains=query, is_up=is_up, rep=rep, search=search, 
		never_seen=never_seen, more=more, show_subdomains=show_subdomains, show_fh_default=show_fh_default, n_results=n_results)
	

@app.route('/json')
@db_session
def json():
	now = datetime.now()
	event_horizon = now - timedelta(days=30)
	domains = Domain.select(lambda p: p.last_alive > event_horizon).order_by(desc(Domain.created_at))
	out = []
	for domain in domains:
		d = dict()
		d['url']        = domain.index_url()
		d['title']      = domain.title
		d['is_up']      = domain.is_up
		d['created_at'] = domain.created_at
		d['visited_at'] = domain.visited_at
		d['last_seen']  = domain.last_alive
		d['is_genuine'] = domain.is_genuine
		d['is_fake']    = domain.is_fake

		if domain.ssh_fingerprint:
			d['ssh_fingerprint']  = domain.ssh_fingerprint.fingerprint
		else:
			d['ssh_fingerprint']  = None

		out.append(d)

	return jsonify(out)

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
	emails = domain.emails()
	bitcoin_addresses = domain.bitcoin_addresses()
	if domain.ssh_fingerprint:
		fp_count = len(domain.ssh_fingerprint.domains)
	if domain:
		links_to   = domain.links_to()
		links_from = domain.links_from()
		return render_template('onion_info.html', domain=domain, emails=emails, bitcoin_addresses=bitcoin_addresses, links_to=links_to, links_from = links_from, fp_count=fp_count)
	else:
		return render_template('error.html', code=404, message="Onion not found."), 404


@app.route('/onion/<onion>/json')
@db_session
def onion_info_json(onion):
	links_to = []
	links_from = []
	domain = select(d for d in Domain if d.host==onion).first()
	if not domain:
		return render_template('error.html', code=404, message="Onion not found."), 404

	links_to   = domain.links_to()
	links_from = domain.links_from()
	emails     = domain.emails()
	btc_addr   = domain.bitcoin_addresses()
	d = dict()
	d['url']        = domain.index_url()
	d['title']      = domain.title
	d['is_up']      = domain.is_up
	d['created_at'] = domain.created_at
	d['visited_at'] = domain.visited_at
	d['last_seen']  = domain.last_alive
	d['is_genuine'] = domain.is_genuine
	d['is_fake']    = domain.is_fake
	d['links_to']   = []
	d['links_from'] = []
	d['emails']     = []
	d['bitcoin_addresses'] = []
	if domain.ssh_fingerprint:
		d['ssh_fingerprint']  = domain.ssh_fingerprint.fingerprint
	else:
		d['ssh_fingerprint']  = None

	for link_to in links_to:
		d['links_to'].append(link_to.index_url())
	for link_from in links_from:
		d['links_from'].append(link_from.index_url())
	for email in emails:
		d["emails"].append(email.address)
	for addr in btc_addr:
		d["bitcoin_addresses"].append(addr.address)

	return jsonify(d)

@app.route('/ssh/<id>')
@db_session
def ssh_list(id):
	fp = SSHFingerprint.get(id=id)
	if fp:
		domains = fp.domains
		fingerprint = fp.fingerprint
		return render_template('ssh_list.html', domains=domains, fingerprint=fingerprint)
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

@app.route('/bitcoin/<addr>')
@db_session
def bitcoin_list(addr):
	btc_addr = BitcoinAddress.get(address=addr)
	if btc_addr:
		domains = btc_addr.domains()
		return render_template('bitcoin_list.html', domains=domains, addr=addr)
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