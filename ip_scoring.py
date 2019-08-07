import threading


"""
wsWall MIS (management and intelligence server)

speichert individuelle ip acl online; wswall waf node pulled die liste

Bsp.: MIS erkennt abuseIP im Zugriffslog. MIS beurteilt anhand diverser Parameter die IP-Reputation. MIS entscheidet die IP zu blocken.
"""



# kann verwendet werden fuer: loginfos, status infos, temporaere ip blockings, scoring etc.
# score <= 0 is good ; >= 1 bad
# if score is >= 3 block 10min ; your ip is blocked because of bad 
# ip reputation score
# geoip score?!
# anomali im request
# anomali bei der angefragten ressource: bsp.: es wird eine iis ressource auf einem apache angefragt
# if session cookie in request - better score?!


# attack typen: brute force wahlos und viele anfragen count der 404 Meldungen
# gezielter sqli: anomali im request 
# gezielter xss: anomali im request
# viel 404 == block

# BAD IP OSINT: http://iplists.firehol.org/?ipset=bi_bruteforce_0_1d



#IP_LIST = ["1.1.1.1","2.2.2.2"]
#IP_SCORE = [0,3]


IP_LIST = []
IP_SCORE = []


def remove_ip_scoring(ip):
	for i in range(len(IP_LIST)):
		if ip in IP_LIST[i]:
			IP_LIST[i] = ""
			IP_SCORE[i] = ""


def increment_ip_scoring(ip):
        for i in range(len(IP_LIST)):
                if ip in IP_LIST[i]:
                        if IP_SCORE[i] <= 60:
                                SCORE = IP_SCORE[i] +1
                                IP_SCORE[i] = SCORE
		else:
        		IP_LIST.append(ip)
        		IP_SCORE.append(1)


def decrement_ip_scoring(ip):
        for i in range(len(IP_LIST)):
                if ip in IP_LIST[i]:
			if IP_SCORE[i] >= 1:
                        	SCORE = IP_SCORE[i] -1 
                        	IP_SCORE[i] = SCORE


def add_ip_scoring_value(ip,value):
	IP_LIST.append(ip)
	IP_SCORE.append(value)


def show_ip_scoring_list():
	for i in range(len(IP_LIST)):
		print(IP_LIST[i])
		print(IP_SCORE[i])


#prueft ob eine ip eine schlechte reputation hat
def is_ip_bad(ip):
	is_bad=False
        for i in range(len(IP_LIST)):
                if ip in IP_LIST[i]:
                        if IP_SCORE[i] >= 2:
				is_bad=True
	return is_bad



#decrement all scores in list
def decrement_ip_scoring_all():
        for i in range(len(IP_LIST)):
        	if IP_SCORE[i] >= 1:
                	SCORE = IP_SCORE[i] -1
                        IP_SCORE[i] = SCORE



#show_ip_scoring_list()
#remove_ip_scoring("1.1.1.1")
#add_ip_scoring_value("4.4.4.4",0)
#add_ip_scoring_value("1.1.1.1",0)
#increment_ip_scoring("1.1.1.1")
#increment_ip_scoring("1.1.1.1")
#increment_ip_scoring("1.1.1.1")
#decrement_ip_scoring("1.1.1.1")




def dec_ip_score():
	threading.Timer(5.0, dec_ip_score).start()
	decrement_ip_scoring_all()
	#show_ip_scoring_list()



#decrement timer to - resozialisieren
dec_ip_score()
