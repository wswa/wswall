import re
def http_recv(http_data):
        pattern = "GET "
        str_found = http_data.find(pattern)


        if str_found >= 0:
                first_line = http_data.split('\n')[0]
                print "FOUND: ", first_line

		req_path = first_line.split()	
		req_path = req_path[1]

		print "PATH:", req_path

		#replace path


                if "/wslab/" in req_path:
                       print "REPLACED PATH"
                       http_data = re.sub(r"/wslab/", "/xss/", http_data, 1)
                       #print "DATA: ", http_data
		else:
			print "WHITELISTING - BLOCK OTHER REQUESTS"



		#if req_path == "/":
		#	print "REPLACED PATH"
                #	http_data = re.sub(r"/", "/xss/", http_data, 1)
                #	#print "DATA: ", http_data


                #if "/js/" in req_path:
                #        print "REPLACED PATH"
                #        http_data = re.sub(r"/js/", "/xss/js/", http_data, 1)
                #        #print "DATA: ", http_data


                #if "/css/" in req_path:
                #        print "REPLACED PATH"
                #        http_data = re.sub(r"/css/", "/xss/css/", http_data, 1)
                #        #print "DATA: ", http_data

                #if "/img/" in req_path:
                #        print "REPLACED PATH"
                #        http_data = re.sub(r"/img/", "/xss/img/", http_data, 1)
                #        #print "DATA: ", http_data


        return http_data
