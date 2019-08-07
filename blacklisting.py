import re #import our regex module
import urllib as url
import wlog 





#decoding
def decoding(input_string):
	n=3
	i=1
	while i <= n:
		text = url.unquote(input_string)
		i=i+1
	return text


#clean tags
def cleantags(input_string):
	text = re.sub('<.*?>', ' ', input_string)
	return text


#badsigs blacklist
#auslagern aus funktion - performanz
inputfile = "db_general.sig"
blacklist_array = []
with open(inputfile) as my_file:
    for line in my_file:
	line = line.rstrip('\n')
	blacklist_array.append(line)


#badsigs blacklist -- command execute
inputfile_command_execution = "db_command_execution.sig"
#inputfile_command_execution = "test.txt"
blacklist_array_command_execution = []
with open(inputfile_command_execution) as my_file:
    for line in my_file:
	line = line.rstrip('\n')
        blacklist_array_command_execution.append(line)

#badsigs blacklist -- sqli 
inputfile_sqli = "db_sqli.sig"
blacklist_array_sqli = []
with open(inputfile_sqli) as my_file:
    for line in my_file:
	line = line.rstrip('\n')
        blacklist_array_sqli.append(line)

#badsigs blacklist -- xml 
inputfile_xml = "db_xml.sig"
blacklist_array_xml = []
with open(inputfile_xml) as my_file:
    for line in my_file:
	line = line.rstrip('\n')
        blacklist_array_xml.append(line)


print "[+] Load Blacklisting pattern"
print "Blacklist pattern count (GLOBAL): ", len(blacklist_array)
print "Blacklist pattern count (COMMAND EXECUTION): ", len(blacklist_array_command_execution)
print "Blacklist pattern count (SQLI): ", len(blacklist_array_sqli)
print "Blacklist pattern count (XML): ", len(blacklist_array_xml)





def blacklisting(input_string, clientip):
	#print "CHECK-BL",input_string
        for signature in blacklist_array:
                bl_search = re.search(signature[7:], input_string)
                if bl_search is not None:
                        message = "BLACKLISTING-PATTERN-MATCH BL-GLOBAL-PATTERN " +  bl_search.group() + " " + signature[7:] + " " + signature[:6]
			wlog.sendlog_message(message, clientip, input_string, "warn")
                        return signature[:6] 


	for signature in blacklist_array_command_execution:
		bl_search_ce = re.search(signature[7:], input_string)
        	if bl_search_ce is not None:
                	message = "BLACKLISTING-PATTERN-MATCH BL-COMMAND-EXECUTION " +  bl_search_ce.group() + " " + signature[7:] + " " + signature[:6]
			wlog.sendlog_message(message, clientip, input_string, "warn")
                	return signature[:6] 


        for signature in blacklist_array_sqli:
                bl_search_sqli = re.search(signature[7:], input_string)
                if bl_search_sqli is not None:
                        message = "BLACKLISTING-PATTERN-MATCH BL-COMMAND-SQLI " +  bl_search_sqli.group() + " " + signature[7:] + " " + signature[:6]
			wlog.sendlog_message(message, clientip, input_string, "warn")
                        return signature[:6] 


        for signature in blacklist_array_xml:
                bl_search_xml = re.search(signature[7:], input_string)
                if bl_search_xml is not None:
                        message = "BLACKLISTING-PATTERN-MATCH BL-COMMAND-XML " +  bl_search_xml.group() + " " + signature[7:] + " " + signature[:6]
			wlog.sendlog_message(message, clientip, input_string, "warn")
                        return signature[:6] 

	return 0 




