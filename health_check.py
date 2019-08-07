import urllib

try:
	print urllib.urlopen("https://wslab.de/xss/").getcode()
except:
	print "OFFLINE"
