import re

def http_recv(http_data):

        pattern = " 404 "
        str_found = http_data.find(pattern)
        if str_found >= 0:
                first_line = http_data.split('\n')[0]
                print "FOUND: ", first_line
                http_data = re.sub(r"404 Not Found", "200 OK", http_data, 1)
                print "DATA: ", http_data
	return http_data
