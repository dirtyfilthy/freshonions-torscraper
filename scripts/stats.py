 #!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
from operator import itemgetter
import sys 
from tabulate import tabulate

@db_session
def list_stats():
	data = list(DailyStat.get_stats().iteritems())
	print(tabulate( sorted(data, key=itemgetter(0)) ))


list_stats()
sys.exit(0)