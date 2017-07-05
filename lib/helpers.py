from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import url_for
from flask import redirect
from flask import send_from_directory
import urlparse
import dateutil.parser
from pony.orm import *
from datetime import *
from tor_db import *
from tor_elasticsearch import *
from tor_cache import *
import re
import os
import bitcoin
import email_util
import banned
import tor_text
import urllib

@db_session
def render_elasticsearch(context, json=False):
	result_limit = int(os.environ['RESULT_LIMIT'])
	page = context["page"]
	sort = context["sort"]
	results = elasticsearch_pages(context, sort, page)
	orig_count = results.hits.total
	n_results  = result_limit if orig_count > result_limit else orig_count
	is_more = (orig_count > result_limit)

	domain_set_dict = dict()
	for hit in results.hits:
		domain_set_dict[hit.domain_id] = True
	domain_set = domain_set_dict.keys()
	domain_precache = select(d for d in Domain if d.id in domain_set)
	if json:
		return (json_elastic_search_results(results, context, orig_count), orig_count)
	else:
		return (render_template('index_fulltext.html', results=results, context=context, orig_count=orig_count, n_results=n_results, page=page, per_page=result_limit, sort=sort, is_more = is_more), orig_count)


@db_session
def maybe_domain_search(context, json=False):
	page = context["page"]
	sort = context["sort"]
	search = context["search"].strip()
	result_limit = int(os.environ['RESULT_LIMIT'])
	if context["search_title_only"] or search == "":
		query = build_domain_query(context)
		orig_count = count(query)
		n_results  = result_limit if orig_count > result_limit else orig_count
		query = query.page(page, result_limit)
		is_more = (orig_count > result_limit)
		
		if json:
			return (json_domain_search_results(query, context, orig_count), orig_count)
		else:
			return (render_template('index_domains_only.html', domains=query, context=context, orig_count=orig_count, n_results=n_results, per_page=result_limit, page=page, sort=sort, is_more = is_more), orig_count)
	return (None, 0)

def maybe_search_redirect(search):
	search = search.strip()
	if Domain.is_onion_url(search):
		parsedurl = urlparse.urlparse(search)
		search = parsedurl.hostname
	if search != "":
		if re.match('.*\.onion$', search):
			return redirect(url_for("onion_info",onion=search), code=302)
		elif re.match(email_util.REGEX_ALL, search):
			return redirect(url_for("email_list",addr=search), code=302)
		elif bitcoin.is_valid(search):
			return redirect(url_for("bitcoin_list",addr=search), code=302)
	return None

def build_search_context():
	context = dict()
	context["is_up"] = request.args.get("is_up")
	context["rep"] = request.args.get("rep")
	context["show_subdomains"] = request.args.get("show_subdomains")
	context["show_fh_default"] = request.args.get("show_fh_default")
	context["search"] = request.args.get("search")
	context["never_seen"] = request.args.get("never_seen")
	context["more"] = request.args.get("more")
	context["phrase"] = request.args.get("phrase")

	context["search_title_only"] = "on" if (not is_elasticsearch_enabled() or request.args.get("search_title_only")) else None
	page = int(request.args.get("page", 1))
	if page < 1:
		page = 1
	context["page"] = page

	if not context["search"]:
		context["search"] = ""
	context["search"] = context["search"].strip()
	context["raw_search"] = context["search"]
	context["search"] = banned.delete_banned(context["search"])

	if not context["rep"]:
		context["rep"] = "n/a"

	context["sort"] = request.args.get("sort")
	return context

@db_session 
def count_ports(port):
	return cache_memoize("count.ports:%d" % port, timeout=3600, func=lambda: OpenPort.count_open(port))

@db_session 
def count_emails(email):
	return cache_memoize("count.emails:%s" % email.address, timeout=3600, func=lambda: len(email.domains()))

@db_session 
def count_bitcoins(addr):
	return cache_memoize("count.bitcoin:%s" % addr.address, timeout=3600, func=lambda: len(addr.domains()))

@db_session 
def count_paths(path):
	return cache_memoize("count.paths:%s" % path, timeout=3600, func=lambda: len(Domain.domains_for_path(path)))

@db_session
def count_webcomponent(name, version=None, account=None, string=None):
	return cache_memoize(("count.webcomponent:%s;%s;%s;%s" % (str(name).replace(' ', '_'), str(version).replace(' ', '_'), str(account).replace(' ', '_'), str(string).replace(' ', '_'))), timeout=3600, func=lambda: len(WebComponent.find_domains(name, version=version, string=string, account=account)))

def build_domain_query(context):
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

	sort = context["sort"]
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

def next_index_page_url(context, n_results):
	result_limit = int(os.environ['RESULT_LIMIT'])
	if (result_limit * context['page']) > n_results:
		return None
	url="http://%s/json?" % os.environ['SITE_DOMAIN']
	nc = dict(context)
	nc["page"] += 1
	first=True
	for k in nc:
		v = str(nc[k]).strip()
		if v == '' or nc[k] is None:
			continue
		if not first:
			url=url+"&"
		url=url+( "%s=%s" % (k, urllib.quote(v)) )
		first=False
	return url


def json_domain_search_results(results, context, n_results):
	json_obj = dict()
	result_limit = int(os.environ['RESULT_LIMIT'])
	json_obj["total_results"] = n_results
	json_obj["next_page"] = next_index_page_url(context, n_results)
	json_obj["query"] = context
	json_obj["results"] = map(lambda d: {"domain":d.to_dict(), "url":d.index_url(), "title":d.title, "fragment":None, "created_at":d.created_at, "visited_at":d.visited_at}, list(results))
	return jsonify(json_obj)

@db_session
def json_elastic_search_results(results, context, n_results):
	json_obj = dict()
	result_limit = int(os.environ['RESULT_LIMIT'])
	json_obj["total_results"] = n_results
	json_obj["next_page"] = next_index_page_url(context, n_results)
	json_obj["query"] = context
	ary = []
	for hit in results.hits:
		domain = Domain.to_dict(Domain.get(id=hit.domain_id))
		url = hit.meta.id
		title = hit.title
		fragment = hit.meta.highlight.body_stripped[0]
		created_at = dateutil.parser.parse(hit.visited_at)
		visited_at = dateutil.parser.parse(hit.created_at)
		ary.append({"domain":domain, "url":url, "title":title, "fragment":fragment, "created_at":created_at, "visited_at":visited_at})
	json_obj["results"] = ary
	return jsonify(json_obj)

def is_json_route():
	rule = request.url_rule.rule
	if re.match(".*?/json$", rule):
		return True
	return False