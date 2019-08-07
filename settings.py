import ConfigParser

#CONFIG PARSER
config = ConfigParser.ConfigParser()
config.optionxform = str

#CONFIG PARSER
def config_init(configfile):
        config.read(configfile)
        global HOSTNAME_SERVERSIDE
        HOSTNAME_SERVERSIDE = config.get('BASIC', 'HOSTNAME_SERVERSIDE')

        global DEBUG_LOG 
        DEBUG_LOG = config.get('BASIC', 'DEBUG_LOG')

        global SCRIPT 
	try:
        	SCRIPT = config.get('BASIC', 'SCRIPT')
	except:
		SCRIPT = ""
		pass

        global PROXYONLY 
        PROXYONLY = config.get('BASIC', 'PROXYONLY')

        global LOGFILE 
        LOGFILE = config.get('BASIC', 'LOGFILE')

        global SSL_SERVERSIDE
        SSL_SERVERSIDE = config.get('BASIC', 'SSL_SERVERSIDE')

        global CERT
        CERT = config.get('SSL', 'CERTIFICATE')

        global KEY
        KEY = config.get('SSL', 'KEY')

        global SSL_ON 
        SSL_ON = config.get('SSL', 'SSL_ON')

        global HTTP_HTTPS_REDIRECT 
        HTTP_HTTPS_REDIRECT = config.get('SSL', 'HTTP_HTTPS_REDIRECT')

        global IP_SERVERSIDE
        IP_SERVERSIDE = config.get('BASIC', 'IP_SERVERSIDE')

	global SERVER_IP
	SERVER_IP = config.get('BASIC', 'SERVER_IP')

        global PORT_SERVERSIDE
        PORT_SERVERSIDE = config.getint('BASIC', 'PORT_SERVERSIDE')

        global SERVER_PORT
        SERVER_PORT = config.getint('BASIC', 'SERVER_PORT')

        global WORKERS 
        WORKERS = config.getint('BASIC', 'WORKERS')

        global NOT_ALLOWED_METHODS
        NOT_ALLOWED_METHODS = config.get('HTTP', 'NOT_ALLOWED_METHODS').split(',')

        global BLOCKED_URLS
        BLOCKED_URLS = config.get('HTTP', 'BLOCKED_URLS').split(',')

        global CIPHERS
        CIPHERS = config.get('SSL', 'CIPHERS')

        global BLOCKED_IPS
        BLOCKED_IPS = config.get('IP', 'BLOCKED_IPS').split(',')

        global SECURITY_MODE
        SECURITY_MODE = config.get('SECURITY', 'SECURITY_MODE')

        global SYSLOG_ACTIVATE
        SYSLOG_ACTIVATE = config.get('BASIC', 'SYSLOG_ACTIVATE')

        global SYSLOG_IP
        SYSLOG_IP = config.get('BASIC', 'SYSLOG_IP')

	global RULE_EXCEPTIONS
	RULE_EXCEPTIONS = config.get('SECURITY', 'RULE_EXCEPTIONS').split(',')

	global IP_SCORING 
	IP_SCORING = config.get('SECURITY', 'IP_SCORING')

def config_write_blocked_ips(configfile):
	cfgfile = open(configfile,'w')

	BLOCKED_IPS_STR = ','.join(map(str, BLOCKED_IPS))

	# add the settings to the structure of the file, and lets write it out...
	#config.add_section('Person')
	config.set('IP','BLOCKED_IPS',BLOCKED_IPS_STR)
	config.write(cfgfile)
	cfgfile.close()
