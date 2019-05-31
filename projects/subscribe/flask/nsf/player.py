from settings import Settings
from map_mod import Map
import socket
import json
from random import randrange
class Player(object):
	
	def __init__(self, coords):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.coords = coords
		self.destination = None
		#self.view_map = Map.get_local_map(coords, Settings.radius) #view map returns the map of node and edges based on how far the players can see\
		#get local map needs to be on its own thread update gradually eventually not important for simulation
		self.client.connect(('127.0.0.1', 25000))
		self.update_map_request()
	def __call__(self):
		while True:
			data = self.client.recv(1024)
			print('im here yeee')
			print(data)



	def update_map_request(self):
		data = {'title':'update', 'coord':self.coords}
		self.client.send(json.dumps(data).encode())
		#self.client.send("I am CLIENT\n".encode())
		from_server = json.loads(self.client.recv(4096).decode())['coord']
		#self.client.close()
		print(from_server)
		#print(json.loads(from_server.decode())['title'])


if __name__ == '__main__':
	play = Player((randrange(100),randrange(100)))
	play()