#!/usr/bin/python
import socket
import paramiko
import hashlib
import base64
import sys
 
if len(sys.argv) != 2:
    print "Usage: %s <ip>" % sys.argv[0]
    quit()
 
try:
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.connect((sys.argv[1], 22))
except socket.error:
    print "Error opening socket"
    quit()
 
try:
    myTransport = paramiko.Transport(mySocket)
    myTransport.start_client()
    sshKey = myTransport.get_remote_server_key()
except paramiko.SSHException:
    print "SSH error"
    quit()
 
myTransport.close()
mySocket.close()
 
 
printableType = sshKey.get_name()
printableKey = base64.encodestring(sshKey.__str__()).replace('\n', '')
sshFingerprint = hashlib.md5(sshKey.__str__()).hexdigest()
printableFingerprint = ':'.join(a+b for a,b in zip(sshFingerprint[::2], sshFingerprint[1::2]))
print(printableType+" "+printableKey)
