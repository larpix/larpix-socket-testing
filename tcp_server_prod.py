#

import socket
import time

# This will serve as the interface to the chip handler. Interaction via TCP/IP is simple.
# it will start a server listening on PORTNUM and will control and respond to the 
# chip handler as needed. 
# it will open up the listening socket and wait for the chip handler to initiate connection
# The chip handler will start the conversation with "H\r", Hello, I presume
# the chip handler wairs for the tester to reply with "R\r", Ready.
# the chip handler moves the next chip to the test socket and will say 
# "S1\r" Socket 1 is ready. (only one socket for us.)
# The tester will do it's testing, or simulated testing and return
# a Result like "RN\r", where N is the test result. N=1 is good, N!=1 is bad of type N

# Not sure how the Handler says it is out of chips, or anything like that.

#HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
#HOST = '192.168.12.138'  # apdlab pc interface address 
#PORT = 38630  # Port to listen on (non-privileged ports are > 1023)

Hello='H\r'
Start='S\r'
Ready='R\r'
EOL='EOL\r'
Result0='0\r'
Result1='1\r'
Result2='2\r'
Result3='3\r'
Result4='4\r'
Result5='5\r'
Result6='6\r'
Result7='7\r'
Result8='8\r'
Result9='9\r'

def DumbFunc(n):
	#print('I am a dumb function ',n)
	return

def OpenSocketConn(HOST,PORT):
	print('Starting TCPIP server connection')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST,PORT))
	s.listen()
	conn, addr = s.accept()
	print('Connected by', addr)
	return conn,addr

def SendSocketReply(conn,Reply):
		print('Sending ',Reply,' to Chip Handler')
		conn.sendall(bytes(Reply,"utf-8"))

def CheckSocketForData (conn):
	Hello='H\r'
	Start='S\r'
	Ready='R\r'
	EOL='EOL\r'
	Result0='0\r'
	Result1='1\r'
	Result2='2\r'
	Result3='3\r'
	Result4='4\r'
	Result5='5\r'
	Result6='6\r'
	Result7='7\r'
	Result8='8\r'
	Result9='9\r'
	if conn.fileno() <0 : # Check if socket is open
		return
	data = conn.recv(1024)
	if data == bytes(Hello,"utf-8") :
		print('Received Hello from Chip Handler')
		#Send Ready (or EOL) back
		#print('Sending Ready to Chip Handler')
		#conn.sendall(bytes(Ready,"utf-8"))
		return data
	elif data == bytes(Start,"utf-8") :
		print('Received Start from Chip Handler')
		return data
	elif not data : 
		time.sleep(0.1) # just empty waiting, do nothing
		#print('waiting... conn=',conn)
		print('waiting...')
		print('Getting nothing, closing connection')
		conn.close()
		return
	else  :
		print('Received unknown ', data, ' as data')
	return

