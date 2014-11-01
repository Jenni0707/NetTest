import sys
import urllib
import time
               
print "argc:%s" % len(sys.argv);
print "argv:%s" % sys.argv[1:];

if len(sys.argv)>1 :
	url = sys.argv[1]

	filename = 'NetMoniterTest_'+time.strftime('%Y%m%d%H%M%S')
				   
	print "downloading with urllib"
	urllib.urlretrieve(url, filename)
else:
	print 'at least include one argv'
