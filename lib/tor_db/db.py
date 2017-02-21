import os
from pony.orm import *
db = Database()
db.bind('mysql', host=os.environ['DB_HOST'], user=os.environ['DB_USER'], passwd=os.environ['DB_PASS'], db=os.environ['DB_BASE'])