from concurrent.futures import ThreadPoolExecutor as pool
import asyncio
from socket import *

async def async_task():
	pass


def thread_function(c, new_loop):
	asyncio.set_event_loop(new_loop)
	try:
		while True: 
			# data received from client 
			data = c.recv(1024) 
			if not data:
				break
			# reverse the given string from client
			print(data) 
			#data = data[::-1] 
			#new_loop.run()

			new_loop.run_until_complete(async_task())
			# send back reversed string to client 
			c.send(data) 

		# connection closed 
		c.close()
	except Exception as e:
		print(e)


def server(address):
	new_loop = asyncio.new_event_loop()
	sock =socket(AF_INET, SOCK_STREAM) #define socket
	#sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  #setting socket option
	sock.bind(address)  #bind the socket to ip and port
	sock.listen(10)
	#sock.setblocking(False)

	thread_pool = pool(5)

	while True:
		print('listening')
		c, addr = sock.accept()
		thread_pool.submit(thread_function, c, new_loop)


if __name__ == "__main__":
	server(('127.0.0.1', 25000))