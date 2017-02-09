from Crypto.Hash import SHA256
import re
import math

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58decode(v, length):
  	""" decode v into a string of len bytes                                                                                                                            
  	"""
  	long_value = 0L
  	for (i, c) in enumerate(v[::-1]):
  		long_value += __b58chars.find(c) * (__b58base**i)

  	result = ''
  	while long_value >= 256:
    	div, mod = divmod(long_value, 256)
    	result = chr(mod) + result
    	long_value = div
  		result = chr(long_value) + result

  	nPad = 0
  	for c in v:
    	if c == __b58chars[0]: nPad += 1
    	else: break

  	result = chr(0)*nPad + result
  	if length is not None and len(result) != length:
    	return None

  	return result


def is_valid(klass, addr):
	addr=addr.strip()
    if not re.match(r"^[13][a-zA-Z1-9]{26,34}$", addr):
    	return False
    bin_addr = b58decode(addr,25)
  	if bin_addr is None: 
  		return None
  	version  = bin_addr[0]
  	checksum = bin_addr[-4:]
  	vh160    = bin_addr[:-4] # Version plus hash160 is what is checksummed                                                                                                    
  	h3 = SHA256.new(SHA256.new(vh160).digest()).digest()
    if h3[0:4] == checksum:
    	return True
    return False
