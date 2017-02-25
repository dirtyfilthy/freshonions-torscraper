#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 

DailyStat.new_day()
sys.exit(0)