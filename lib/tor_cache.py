from flask import Flask
from flask import request
from flask import g
from flask import render_template
from werkzeug.contrib.cache import MemcachedCache
import os
import functools 

CACHE_TIMEOUT = 60 * 60 * 24 * 365

_cache = None
if os.environ['MEMCACHED_ENABLED'] == "true":
	_cache = MemcachedCache(['%s:%s' % (os.environ['MEMCACHED_HOST'], os.environ['MEMCACHED_PORT'])])

_is_cached = False

class cached(object):

    def __init__(self, timeout=0):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
    	@functools.wraps(f)
        def my_decorator(*args, **kwargs):
        	global _is_cached
        	_is_cached = True
        	if _cache is None:
        		return f(*args, **kwargs)
        	response = _cache.get(request.full_path)
        	if response is None:
        		response = f(*args, **kwargs)
        		_cache.set(request.path, response, self.timeout)
        	_is_cached = False
        	return "%s%s%s" % (render_template("layout_header.html"), response, render_template("layout_footer.html"))

        functools.update_wrapper(my_decorator, f)
        return my_decorator

def is_cached():
	return _is_cached

def clear():
	if _cache is not None:
		_cache.clear()

def invalidate_cache(obj):
	if _cache is None:
		return None
	path_attr = getattr(obj, "canonical_path", None)
	if not callable(path_attr):
		return None
	path = obj.canonical_path()
	_cache.delete(path)
	_cache.delete("%s/json" % path)
	return path



