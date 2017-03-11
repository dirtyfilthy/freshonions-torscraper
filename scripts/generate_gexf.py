#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import networkx
import sys 

@db_session
def get_domains_ids():
	event_horizon = datetime.now() - timedelta(hours=24)
	domain_ids = select(d.id for d in Domain if d.last_alive > event_horizon)
	return list(domain_ids)


@db_session
def build_graph():
	graph = networkx.DiGraph()
	domain_ids = get_domains_ids()
	total = len(domain_ids)
	i = 0
	seen = dict()
	for d_id in domain_ids:
		i += 1
		domain     = Domain.get(id=d_id)
		links_from = domain.links_from()
		commit()
		if domain.host not in seen:
			graph.add_node(domain.host)
			seen[domain.host] = True
		
		for link in links_from:
			if link.host not in seen:
				graph.add_node(link.host)
				seen[link.host] = True
			graph.add_edge(domain.host, link.host) 

		if (i % 10) == 0:
			print("Processed %d / %d" % (i, total))

	return graph

if len(sys.argv) < 2:
	print("Usage %s filename.gexf", sys.argv[0])
	sys.exit(1)

print("Building graph...")
graph = build_graph()
print("Saving '%s'..." % sys.argv[1])
networkx.write_gexf(graph, sys.argv[1])

sys.exit(0)