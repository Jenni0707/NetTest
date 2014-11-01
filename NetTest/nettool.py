import sys
import urllib
import time
               
print "argc:%s" % len(sys.argv);
print "argv:%s" % sys.argv[1:];

if len(sys.argv)>2 :
	url = sys.argv[1]
	filename = sys.argv[2]
				   
	print "downloading with urllib"
	urllib.urlretrieve(url, filename)
else:
	print 'nettool usage : nettool url filename'
