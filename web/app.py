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
import re
import os
import bitcoin
import email_util
import banned
app = Flask(__name__)
app.jinja_env.globals.update(Domain=Domain)
app.jinja_env.globals.update(NEVER=NEVER)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(select=select)

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


def build_domain_query(context, sort):
	query = select(d for d in Domain)
	search = context["search"]
	query = query.filter("d.is_banned == 0")
	if search !='':
		query = query.filter("search in d.title")

	if context["is_up"]:
		query = query.filter("d.is_up == 1")
	
	if context["rep"] == "genuine":
		query = query.filter("d.is_genuine == 1")
	if context["rep"] == "fake":
		query = query.filter("d.is_fake == 1")
	
	if not context["show_subdomains"]:
		query = query.filter("d.is_subdomain == 0")
	
	if not context["show_fh_default"]:
		query = query.filter("d.is_crap == 0")
	
	if not context["never_seen"]:
		query = query.filter("d.last_alive != NEVER")
	
	if   sort=="onion":
		query = query.order_by(Domain.host)
	elif sort=="title":
		query = query.order_by(Domain.title)
	elif sort=="last_seen":
		query = query.order_by(desc(Domain.last_alive))
	elif sort=="visited_at":
		query = query.order_by(desc(Domain.visited_at))
	else:
		query = query.order_by(desc(Domain.created_at))

	return query

@app.route("/")
@db_session
def index():
	result_limit = int(os.environ['RESULT_LIMIT'])
	max_result_limit = int(os.environ['MAX_RESULT_LIMIT'])
	now = datetime.now()

	context = dict()
	context["is_up"] = request.args.get("is_up")
	context["rep"] = request.args.get("rep")
	context["show_subdomains"] = request.args.get("show_subdomains")
	context["show_fh_default"] = request.args.get("show_fh_default")
	context["search"] = request.args.get("search")
	context["never_seen"] = request.args.get("never_seen")
	context["more"] = request.args.get("more")
	context["search_title_only"] = "on" if (not is_elasticsearch_enabled() or request.args.get("search_title_only")) else None

	if not context["search"]:
		context["search"]=""
	context["search"] = context["search"].strip()
	context["search"] = banned.delete_banned(context["search"])

	if not context["rep"]:
		context["rep"] = "n/a"

	sort = request.args.get("sort")

	search = context["search"]
	if search != "":
		if re.match('.*\.onion$', search):
			return redirect(url_for("onion_info",onion=search), code=302)
		elif re.match(email_util.REGEX_ALL, search):
			return redirect(url_for("email_list",addr=search), code=302)
		elif bitcoin.is_valid(search):
			return redirect(url_for("bitcoin_list",addr=search), code=302)
			
	if context["search_title_only"] or search == "":
		query = build_domain_query(context, sort)
		orig_count = count(query)
		n_results  = orig_count
		if not context["more"]:
			query = query.limit(result_limit)
			if n_results > result_limit:
				n_results = result_limit

		is_more = (orig_count > result_limit) and not context["more"]

		return render_template('index_domains_only.html', domains=query, context=context, orig_count=orig_count, n_results=n_results, sort=sort, is_more = is_more)
	
	results = elasticsearch_pages(context, sort)
	orig_count = results.hits.total
	n_results  = orig_count
	n_results  = result_limit if n_results > result_limit and not context["more"] else n_results
	is_more = (orig_count > result_limit) and not context["more"]

	domain_set_dict = dict()
	for hit in results.hits:
		domain_set_dict[hit.domain_id] = True
	domain_set = domain_set_dict.keys()
	domain_precache = select(d for d in Domain if d.id in domain_set)

	return render_template('index_fulltext.html', results=results, context=context, orig_count=orig_count, n_results=n_results, sort=sort, is_more = is_more)



@app.route('/json')
@db_session
def json():
	now = datetime.now()
	event_horizon = now - timedelta(days=30)
	domains = Domain.select(lambda p: p.last_alive > event_horizon and p.is_banned==False).order_by(desc(Domain.created_at))
	out = []
	for domain in domains:
		out.append(domain.to_dict(full=False))

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
	return jsonify(domain.to_dict(full=True))

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