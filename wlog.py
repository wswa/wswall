import datetime
import syslog_client
import settings


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def sendlog_message(message, clientip, fullrequest, typ):
	str_from_time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "on" in settings.SYSLOG_ACTIVATE:
		#send to syslog
                log = syslog_client.Syslog(settings.SYSLOG_IP)
		log.send(str_from_time_now + " " + str(clientip) + " " + message + " " + fullrequest + "\r\n", syslog_client.Level.WARNING)

	if 'info' in typ:
		print bcolors.OKGREEN + str_from_time_now + " " + str(clientip) + " " + message + bcolors.ENDC

        if 'warn' in typ:
                print bcolors.FAIL + str_from_time_now + " " + str(clientip) + " " + message + bcolors.ENDC

	f = open(settings.LOGFILE, 'a')
	f.write(str_from_time_now + " " + str(clientip) + " " + message + "\r\n")
	f.close()


#settings.SYSLOG_ACTIVATE = "on"
#settings.SYSLOG_IP = "127.0.0.1"
#sendlog_message("wsWall_startup","","","info")
#sendlog_message("wsWall_startup","","","warn")
