#!/usr/bin/python
import json
import sys
json_data=open(sys.argv[1]).read()
data = json.loads(json_data)
for hs in data["hidden_services"]:
	print("%s.onion" % hs["id"])