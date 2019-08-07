#!/usr/bin/python -u
# wsWALL 1.0
# Author: marcel bilal
# contact@wswall.com
# all copyrights are reserved - wsWall


import socket
import select
import time
import sys
import re 
import ssl
import settings
import ConfigParser
import wlog
import os
import multiprocessing
import check_version
#import importlib
import imp

oldStdout = sys.stdout
sys.stdout = sys.stderr


print ""
print "wsWALL 1.0"
print ""


#CHECK VERSION
print "[+] Checking Version..."
check_version.checking_version()



#CONFIG PARSER
config = ConfigParser.ConfigParser()

if len (sys.argv) != 2 :
    config.read("config.ini")
    configfile = "config.ini" 
else:
    config.read(sys.argv[1])
    configfile = sys.argv[1]

#lock file
#file = open(configfile + ".lock","w")
#file.close()



#INCLUDE DECODING + BLACKLISTING
from blacklisting import decoding
from blacklisting import blacklisting


#CONFIG PARSER
settings.config_init(configfile)

#workers
# better states with 5 workers on this system, but only dual core
num_workers = settings.WORKERS 

print "[+] CONFIGFILE: ", configfile 
print "[+] SECURITY-MODE: ", settings.SECURITY_MODE

if "1" in settings.IP_SCORING:
	import ip_scoring
	print "[+] IP-SCORING: ", settings.IP_SCORING


if ".py" in settings.SCRIPT:
        print "[+] ACTIVATE SCRIPT: ", settings.SCRIPT 
	global my_mod
	my_mod = imp.load_source('my_script', settings.SCRIPT)



def generate_headers(response_code):
        """
        Generate HTTP response headers.
        Parameters:
            - response_code: HTTP response code to add to the header. 200 and 404 supported
        Returns:
            A formatted HTTP header for the given response_code
        """
        header = ''
        if response_code == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif response_code == 404:
            header += 'HTTP/1.1 404 Not Found\n'

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: {now}\n'.format(now=time_now)
        header += 'Server: wsWall\n'
        header += 'Connection: close\n\n' # Signal that connection will be closed after completing the request
	header += 'Request was blocked by wsWall'
        return header


def run_redirect():
        s = socket.socket()

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #s.bind((host,port))
        s.bind((settings.SERVER_IP,80))
        s.listen(5)

        while True:
            c, addr = s.accept()
            #print("Connection accepted from " + repr(addr[1]))
            data = c.recv(1024)
            #print data
            #host = re.findall(r"Host:.*\r\n", data, re.MULTILINE)
            host = re.search(r"Host: (.+)\r\n",data).group(1) 
            #print host
            hostheader = str(host)
            try:
                #hostname = hostheader.split(":")[1]
                #hostname = hostname.strip()
                #target = "https://" + hostname
		target = "https://" + hostheader
                #print hostname
                sdata = "HTTP/1.1 302 Encryption Required\r\nLocation: " + target + "\r\n"
                c.send(sdata)
                c.close()
            except:
                c.close()
		print "[-] HTTP HTTPS REDIRECT - Error closing socket..."



if "1" in settings.HTTP_HTTPS_REDIRECT:
	print "[+] HTTP HTTPS REDIRECT"
	mp1 = multiprocessing.Process(target=run_redirect, args=())
	mp1.start()


# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001

forward_to = (settings.IP_SERVERSIDE, settings.PORT_SERVERSIDE)


wlog.sendlog_message("wsWall_startup","","","info")




#SERVERSIDE CONNECTION = WAF->SERVER
class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	#self.forward.settimeout(10)
    	#print "Socket timeout: ", self.forward.gettimeout()
	#wenn ssl socket dann
	if "on" in settings.SSL_SERVERSIDE:
	    	context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    		context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
		context.verify_mode = ssl.CERT_OPTIONAL
		context.check_hostname = False
    		self.forward = context.wrap_socket(self.forward, server_hostname=settings.IP_SERVERSIDE)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
	    print "CLIENT SOCKET ERROR"
            print e
            return False

#CLIENTSIDE CONNECTION = CLIENT->WAF
class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	if "1" in settings.SSL_ON:
  		context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  		context.load_cert_chain(certfile=settings.CERT, keyfile=settings.KEY)  # 1. key, 2. cert, 3. intermediates
  		context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
  		context.set_ciphers(settings.CIPHERS)
		self.server = context.wrap_socket(self.server, server_side=True)

       	self.server.bind((host, port))
       	self.server.listen(500)

    def main_loop(self):
	print "PID:" , os.getpid()
	self.input_list.append(self.server)
	while 1:
	    time.sleep(delay)
	    ss = select.select
	    inputready, outputready, exceptready = ss(self.input_list, [], [])
	    for self.s in inputready:
		if self.s == self.server:
		    self.on_accept()
		    break

		self.data = self.s.recv(buffer_size)

		if len(self.data) == 0:
		    #try:
		    self.on_close()
		    #except:
		    #print "ON_CLOSE ERROR"
			#print inputready
			#exit()
		    break
		else:
		    self.on_recv()

    def on_accept(self):
	try:
        	clientsock, clientaddr = self.server.accept()
		#clientsock.settimeout(60)
	except:
		print "Error server accept"
		return

	#maybe a place to check LB AND DECIDE THE NODE

        forward = Forward().start(forward_to[0], forward_to[1])

        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_close(self):
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])

       	out = self.channel[self.s]
       
	try: 
		print self.s.getpeername(), "has disconnected"

	        # close the connection with client
       		self.channel[out].close()  # equivalent to do self.s.close()


        	# close the connection with remote server
        	self.channel[self.s].close()

        	# delete both objects from channel dict
        	del self.channel[out]
        	del self.channel[self.s]
        except:
                print "Error Endpoint not connected?"


    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward


	# SCRIPT MOD
	if ".py" in settings.SCRIPT:
		data = my_mod.http_recv(data)

	#only proxy no waf or filter - highspeed
	if "1" in settings.PROXYONLY:
                self.channel[self.s].send(data)
                return 0
		

	#extract source ip
	sip = str(self.s.getpeername())
	sip = sip.split("'")	
	sip = sip[1]

	#BLOCK IP - ACL
	for IP in settings.BLOCKED_IPS:
		if IP in self.s.getpeername():
			wlog.sendlog_message("BLOCKED_IP",sip,"","warn")
                        return 0

	# raw data
	#print "DATA:", str(data)
	#print ""

        #if "1" in settings.DEBUG_LOG:
        	#print "ORIGINAL-RAW-DATA: ", str(data)
		#wlog.sendlog_message("DEBUG-LOG",str(data),"","info")

    	# parse the first line
    	first_line = data.split('\n')[0]
	http_paket_header = data.split('\r\n\r\n', 1) #split header + content, reicht nicht fuer multipart uploads
	http_paket = data.split('\r\n\r\n') #split header + content

	#print "FULL PAKET:", http_paket
	#print len(http_paket) 
	#print ""

	# parse http responses
        if "HTTP/1" in first_line[0:6]:
		if "1" in settings.DEBUG_LOG:
                	print "RESPONSE-DETECT: ", first_line
			#print "FULL PAKET:", http_paket
			print ""
    		self.channel[self.s].send(data)
		return 0


        # BLOCK SPECIFIC HTTP METHODS - parse http request and check http method
        for httpm in settings.NOT_ALLOWED_METHODS:
                if httpm in first_line.upper():
                        if " HTTP/1" in first_line:
                                print "NOT ALLOWED HTTP METHODE: ", httpm
				wlog.sendlog_message("NOT ALLOWED HTTP METHODE:",sip,"","warn")
                                if "block" in settings.SECURITY_MODE:
                                        return 0


        # BLOCK SPECIFIC URLS - parse http request and check url
        for httpm in settings.BLOCKED_URLS:
                if re.search(httpm, first_line):
                        if " HTTP/1" in first_line:
                                print "NOT ALLOWED URL: ", httpm
                                if "block" in settings.SECURITY_MODE:
					wlog.sendlog_message("BLOCKED_URL",sip,"","warn")
                                        return 0


	# parse and modify header
	if "Host:" in http_paket_header[0]:
		# ersetzt den host im header nur show nicht senden - muss reassambled werden bevor send data
		#http_paket_header = [word.replace('wslab.de','bla.de') for word in http_paket_header]
		#print ""
		#print "PARSE HTTP HEADER"
		#print "HTTP-HEADER: "
		#print http_paket_header[0]
		#print ""

		#NO HEADER MOD+SEC+ETC
                #self.channel[self.s].send(data)
                #return 0

		if settings.HOSTNAME_SERVERSIDE:
			#delete host entry
			data = re.sub(r"Host:.*\r\n", "", data, 1)
			#data = re.sub(r"Accept-Encoding:.*\r\n", "", data, 1)
			#data = re.sub(r"Connection:.*\r\n", "", data, 1)

		# insert x-header nach first line break
		xf_header = "\r\nX-Forwarded-For: " + sip + "\r\n"
		data = re.sub(r"\r\n", xf_header, data, 1)

		#INSERT HEADER MANIPULATION HERE ------>

		if settings.HOSTNAME_SERVERSIDE:
			# insert host nach first line break ----------- MUSS IMMER AM ENDE STEHEN
			host_header = "\r\nHost: " + str(settings.HOSTNAME_SERVERSIDE) + "\r\n"
			data = re.sub(r"\r\n", host_header, data, 1)
			#data = re.sub(r"Host:.*", host_header, data)

		if "1" in settings.DEBUG_LOG:
			print "PAST-HOSTHEADER-REWRITE: ", str(data)
			wlog.sendlog_message("DEBUG-LOG",str(data),"","info")
                        #self.channel[self.s].send(data)
                        #return 0
	

        # parse http requests
        http_methods = ['GET', 'POST', 'HEAD']
        for httpm in http_methods:
                if httpm in first_line:
                        if " HTTP/1" in first_line:
				if "1" in settings.DEBUG_LOG:
					print "PARSE HTTP REQUEST"
					print "REQUEST: ", first_line
					print "FULL PAKET:", http_paket
					print ""
                                decoded_request = decoding(str(http_paket))
				if "1" in settings.DEBUG_LOG:
                                	print "FULL PAKET (decoded):", decoded_request
                                bl_request = blacklisting(decoded_request, self.s.getpeername())
                                #if "BL-REPLACED" in bl_request:
                                if bl_request > 0:
                                        print "ATTACK DETECTED", self.s.getpeername()
                                        print ""

                                        #SCORING
					if "1" in settings.IP_SCORING:
                                        	ip_scoring.add_ip_scoring_value(sip,0)
                                        	ip_scoring.increment_ip_scoring(sip)

                                        	if ip_scoring.is_ip_bad(sip):
							wlog.sendlog_message("BAD_IP_REPUTATION_BLOCK_IP",sip,"","warn")
                                                	settings.BLOCKED_IPS.append(sip)

                                        for rule in settings.RULE_EXCEPTIONS:
                                                if rule in bl_request:
                                                        print "***** EXCEPTION FOR THIS SIGNATUR FOUND ****** SIGNATURE-ID:" + bl_request
							wlog.sendlog_message("EXCEPTION FOR THIS SIGNATUR FOUND" + bl_request,sip,"","warn")
							self.channel[self.s].send(data)
                                			return 0

                                        #BLOCKED_IPS.append(sip) #adds ip to blocked ips

					#IF IN BLOCKING MODE THAN DROP REQUEST - dont send it to the server
                                        if "block" in settings.SECURITY_MODE:
						#dont send to server, but answer the client and drop the connection clean
						response_header = generate_headers(200)
                                		self.channel[self.channel[self.s]].send(response_header)
						self.on_close()
	                                        return 0

                                self.channel[self.s].send(data)
                                return 0

	if "1" in settings.DEBUG_LOG:
		print "FORWARD PAKET ENGINE - chunked or encoded data"
		#print "FULL PAKET:", http_paket
		#print ""
    	self.channel[self.s].send(data)



if __name__ == '__main__':
        server = TheServer(settings.SERVER_IP, settings.SERVER_PORT)
	jobs = []
        try:
            #server.main_loop()
	    print "Spawn workers: ", num_workers
	    for _  in range(num_workers):
    	    	process = multiprocessing.Process(target=server.main_loop, args=())
		jobs.append(process)
    	    	process.start()
        except KeyboardInterrupt:
	    settings.config_write_blocked_ips(configfile)
            print "Ctrl C - Stopping server"
	    #os.remove(configfile + ".lock")
	    wlog.sendlog_message("wsWall_stopped","","","info")
            sys.exit(1)
