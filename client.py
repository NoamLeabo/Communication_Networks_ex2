import socket

# we create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# we create a connection with the TCP server
s.connect(('127.0.0.1', 12345))

# we send teh word hello
s.send(b'hello')

# we wait to receive the data coming from the server
data = s.recv(100)

# we print what we got from the server
print("Server sent: ", data)

# we close the server
s.close()
