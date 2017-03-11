#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 


CloneGroup.delete_empty_groups()
sys.exit(0)