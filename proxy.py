import threading
import base64
import time
import socket
import sys
from datetime import datetime
import signal
dictt={'1.data':[], '2.data':[], '3.data':[],'4.data':[],'5.data':[],'6.data':[],'7.data':[],'8.data':[],'9.data':[]}
dicttt={'1.data':[], '2.data':[], '3.data':[],'4.data':[],'5.data':[],'6.data':[],'7.data':[],'8.data':[],'9.data':[]}
#dictt={'1.dataGET':[], '2.dataGET':[], '3.dataGET':[],'4.dataGET':[],'5.dataGET':[],'6.dataGET':[],'7.dataGET':[],'8.dataGET':[],'9.dataGET':[],
#'1.dataPOST':[], '2.dataPOST':[], '3.dataPOST':[],'4.dataPOST':[],'5.dataPOST':[],'6.dataPOST':[],'7.dataPOST':[],'8.dataPOST':[],'9.dataPOST':[]}
cache=[]
cache_store={'1.data':[], '2.data':[], '3.data':[],'4.data':[],'5.data':[],'6.data':[],'7.data':[],'8.data':[],'9.data':[]}
request_file = open('proxy/requests', 'a+')
response_file = open('proxy/responses', 'a+')
#cache_store={'1.dataGET':[], '2.dataGET':[], '3.dataGET':[],'4.dataGET':[],'5.dataGET':[],'6.dataGET':[],'7.dataGET':[],'8.dataGET':[],'9.dataGET':[],
#'1.dataPOST':[], '2.dataPOST':[], '3.dataPOST':[],'4.dataPOST':[],'5.dataPOST':[],'6.dataPOST':[],'7.dataPOST':[],'8.dataPOST':[],'9.dataPOST':[]}
store_data =  { "IP-HOST" : "127.0.0.1","PROXY_BINDING" : 20100,"ALLOWED_MAX_LEN" : 1024,"CONNECTION_TIMEOUT" : 5}

c=threading.Lock()
class Server:	
    def __init__(self, store_data):
	print "Signal Initializing"
	
        signal.signal(signal.SIGINT, self.close)     
	self.__clients = {}        
	self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	temp =   store_data['IP-HOST']
	temp1 =  store_data['PROXY_BINDING']          
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   
        self.serverSocket.bind((temp,temp1 )) 
        self.serverSocket.listen(10)    
        


    


    def proxy_thread(self, conn, client_addr):
       
        flag2=0
        request = conn.recv(store_data['ALLOWED_MAX_LEN'])  
	request_file.write(request)
	request_file.write('\n')      
	second1 = request.split('\n')        
	first_line = request.split('\n')[0]                  
	hrr = 0    
	print request    
	url = first_line.split(' ')[1]
        #print first_line
        # get url
        #print request
        second_line=request.split('\n')[1]
	#print second_line
        code=second_line.split(' ')[2]
        cred=base64.b64decode(code)
        cred=cred.split(':')
        #print cred
        with open('proxy/Users.txt') as f:
            users=f.readlines()
        users=[x.strip('\n') for x in users]
        flag=0
        for user in users:
            temp=user.split(' ')
            if temp[0]==cred[0] and temp[1]==cred[1]:
                flag=1

        #print flag

        #blacklist=[]
        fname='proxy/blacklist.txt'
        with open(fname) as f:
            blacklist = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        blacklist = [x.strip() for x in blacklist]

        #for i in range(0, len(blacklist)):
        #    if blacklist[i] in url:
        #        conn.close()
        #    return
        # find the webserver and port
        http_pos = url.find("://")          # find pos of ://
	initt= url.find('data')
        if (http_pos==-1):
            temp = url
	    #print initt
	    fla =1
        else:
            temp = url[(http_pos+3):]      
	    fla = 0


        port_pos = temp.find(":")           # find the port pos (if any)

       
        webserver_pos = temp.find("/")
        second2 = 12
        if webserver_pos == -1:
            webserver_pos = len(temp)
        temp2=temp[webserver_pos:len(temp)]
        temp3 = temp2[1:]
        method=first_line.split(' ')[0]

        if(temp3 in cache) and method=='GET':
        	flag2=1
        remaining = '\n'.join(request.split('\n')[1:])

        version=first_line.split(' ')[2]
        top=method+' '+temp2+' '+version
        request='\n'.join([top,remaining])
        if method=='GET' and flag2==0:
            dictt[temp3].append(datetime.now())
	    dicttt[temp3].append(time.time())




        webserver = ""
        serv = []
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):      
            port = 80
            serv.appen(port)
	    webserver = temp[:webserver_pos]
	            
	    fla =1
        else:
            #print (temp[(port_pos+1):])[:webserver_pos-port_pos-1]                                          # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            fla = 0
            webserver = temp[:port_pos]
            serv.append(webserver)
        for x in blacklist:
            if str(x)==str(port):
                print 'true'
                if flag==0:
                    conn.send('\nUnauthenticated user\n')
		    response_file.write('Unauthenticated user')
                    conn.send('Domain Blocked\n')
		    response_file.write('Domain blocked')
                    conn.close()
                    return



        try:
            sent=0
            # create a socket to connect to the web server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(store_data['CONNECTION_TIMEOUT'])
            s.connect((webserver, port))
            if flag2==1:
		print "returned from cache ( succesfully found in cache)"
		temptime=dictt[temp3][len(dictt[temp3])-1]
		MyString = temptime.strftime("%a %b %d %H:%M:%S ")
		ifstat="If-Modified-Since: "+MyString+"GMT "+temptime.strftime("%Y")
		request1='\n'.join(request.split('\n')[2:])
            	request1=top+"\n"+request.split('\n')[1]+"\n"+ifstat+"\n"+request1
		sent=1
		s.sendall(request1)
		print request1
		fir=0
		tempdata=""
		while 1:
			data = s.recv(store_data['ALLOWED_MAX_LEN'])
			if fir==0:
				tempdata=data
				fir=1
			print data			
			if len(data)==0:
				break
		if tempdata.split()[1]=="304":
			print "304"
			print cache
			
		        ir=cache_store[temp3]
		        with open('proxy/cache/'+str(ir),'r') as dataa:
		            x=dataa.read(1024)
		            while len(x)!=0:
		            	conn.send(x)
				response_file.write(x)
		            	x=dataa.read(1024)
		        s.close()
		        conn.close()
		        return
		else:
			print tempdata.split()[1]
			print cache
			s.sendall(request)
		        ir1=cache_store[temp3]
			firs=0
			c.acquire()
			while 1:
		                data = s.recv(store_data['ALLOWED_MAX_LEN'])
				if len(data)>0:
						file1 = 'proxy/cache/'+str(ir1)
						if firs==0:
						    firs=1
						    open(file1, 'w').close()
					    	with open(file1,'a+') as cc:
						    cc.write(data)            		
				else:
					break	
			with open('proxy/cache/'+str(ir),'r') as dataa:
		            x=dataa.read(1024)
		            while len(x)!=0:
		            	conn.send(x)
				response_file.write(x)
		            	x=dataa.read(1024)
		        s.close()
		        conn.close()
		        return	
            		c.release()
            s.sendall(request)

                #print dicttt[temp3],flag2
            flag3=0
            if(len(dicttt[temp3])>2) and method=='GET':
                if((dicttt[temp3][len(dicttt[temp3])-1]-dicttt[temp3][len(dicttt[temp3])-3])<300):
    	            print "eligible for caching"
    	            flag3=1
	    c.acquire()	
            first=0
	    print cache
            print dicttt		
            if(flag3==1):
                if(len(cache)>=3):
                    new_index = cache_store[cache[2]]
                    old_cache = cache[0]
                    cache1 = cache[1]
                    cache[0] = temp3
                    cache[1]=old_cache
                    cache[2]=cache1
                    cache_store[cache[0]]=new_index
                else:
                    cache.append(temp3)
                    cache_store[temp3]=len(cache)
            ir1 = cache_store[temp3]
            length=0
            while 1:
                data = s.recv(store_data['ALLOWED_MAX_LEN'])
                #print data          # receive data from web server
                if( len(data) > 0):
                    #print 'length of data received'
                    #print len(data)
                    
                    conn.send(data)
		    response_file.write(data)
                    #length=length+len(data)
                    #print len(data),length
                    #print data
                                                   # send to browser
                    if flag3==1 :
                    	file1 = 'proxy/cache/'+str(ir1)
                        if first==0:
                            first=1
                            open(file1, 'w').close()
                    	with open(file1,'a+') as cc:
                            cc.write(data)
		            #print cache_store
                    #print cache
                    #print "printed in while loop"
                else:
                    break
	    c.release()
		

            s.close()
            conn.close()
            
        except socket.error as error_msg:
            print 'ERROR: ',client_addr,error_msg
            if s:
                s.close()
            if conn:
                conn.close()


    def _RETURNNAME(self, cli_addr):
        
        return "Client"

    def listenForClient(self):
        while 1:
            (clientSocket, client_address) = self.serverSocket.accept() 
            flag1=0
	    dext = threading.Thread(name=self._RETURNNAME(client_address), target=self.proxy_thread, args=(clientSocket, client_address))
            if(flag1==0):
		tr = 2
	    dext.setDaemon(True)
            dext.start()
        self.serverSocket.close()
	sys.exit(flag1)


    def close(self, signum, frame):
        #print "shutdown server"
        self.serverSocket.close()
        sys.exit(0)


if __name__ == "__main__":
    server = Server(store_data)
    server.listenForClient()
