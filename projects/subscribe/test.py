import socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 25000))
client.send("I am CLIENT\n".encode())
from_server = client.recv(4096)
client.close()
print(from_server)