#!/usr/bin/env python3

import socket
import time

# for larpix testing, the handler will act as the client, so this 
# script should emulate the handler's actions and responses.
# it should send a "H\r" when handler is ready
# If it receives a "R\r" it will send the "start" command
# If it receives a "EOL\r" it will stop testing and exit
# When it has loaded the asic in the socket.  It should look like:
# "S\r" Start testing command for a single test socket.
# the tester will then send the results of the test (bin) to the
# handler, so it knows where to sort it.  
# "1\r" will be success
# all other "N\r" will be failure sort of type N

#HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
HOST = '192.168.12.138'  # apdlab pc interface address 
PORT = 38630        # Port to listen on (non-privileged ports are > 1023)

Hello='H\r'
Start='S\r'
Ready='R\r'
EOL='EOL\r'
Result1='1\r'
Result2='2\r'
Result3='3\r'
Result4='4\r'
Result5='5\r'
Result6='6\r'
Result7='7\r'
Result8='8\r'
Result9='9\r'


print("encode of Hello string")
print(Hello.encode("utf-8").hex())

print("encode of Start string")
print(Start.encode("utf-8").hex())

def get_response(s): 
    data = s.recv(1024)
    if data :
        return data
    time.sleep(0.1) # just empty waiting, do nothing 

#exit()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    connected = s.connect((HOST, PORT))
    print('Connected = ',connected)
    # Still don't have the client syntax quite right here to loop through while connected.
    while s:
    	#s.sendall(b'Hello, world')
    	# Send Hello
        print('Sending Hello')
        s.sendall(bytes(Hello,"utf-8"))
        # loop waiting for responses
        while True:
            data = s.recv(1024)
            #print('Received', repr(data))
            if data == bytes(Ready,"utf-8"):
                print('Received Ready from Tester')
                #Send Start back
                print('Sending Start back')
                s.sendall(bytes(Start,"utf-8"))
                # Wait for result
                Resultbuff = s.recv(1024)
                while not Resultbuff: 
                    Resultbuff = s.recv(1024)
                    time.sleep(0.1)
                print('Got a result of ',Resultbuff,' at ',time.strftime("%H:%M:%S"))
                # start new cycle
                break
            elif data == bytes(EOL,"utf-8") :
                print('Received EOL from Tester, Exiting')
                # Exit
                exit()
            elif not data : 
                time.sleep(0.1) # just empty waiting, do nothing
            else  :
                print('Received unknown ', data, ' as data')

