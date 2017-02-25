import os
PATH = os.environ['ETCDIR'] + "/private/flask.secret"
secret=os.urandom(32)
file = open(PATH, "w")
file.write('FLASK_SECRET="%s"\n' % secret.encode("string-escape"))
print("Written flask secret to '%s'" % PATH)

