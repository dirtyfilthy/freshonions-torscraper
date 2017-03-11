import os
import tor_paths
VERSION_PATH  = tor_paths.ETCDIR + "/version_string"
REVISION_PATH = tor_paths.ETCDIR + "/revision"

def version():
	with open(VERSION_PATH,'r') as f:
		version_string = f.read().strip()
		return version_string

def revision():
	with open(REVISION_PATH,'r') as f:
		revision_string = f.read().strip()
		return int(revision_string)


