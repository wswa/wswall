import urllib2



def checking_version():

	url = "https://install.wswall.com/version"


	try:
		connection = urllib2.urlopen(url)
		statuscode = connection.getcode()
		html = connection.read()
		connection.close()

		if statuscode == 200:
			print "OK"
			print html
		else:
			print "Version check failed!"

	except urllib2.HTTPError, e:
		statuscode = e.getcode()
		print "Version check failed!"


#checking_version()
