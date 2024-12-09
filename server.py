import socket

# we create the socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# we bind the socket woth a specific port of '12345'
server.bind(('', 12345))

# we set the server to listen to at most 5 connections
server.listen(5)

# the endless loop of the server
while True:

    # we accept a 'connect' request that was sent to the server #
    # client_socket - the socket we are gonna communicate with from now on with the current client
    # client_address - the address of the client which we received a request from
    client_socket, client_address = server.accept()
    
    # we print we did we connect with
    print('Connection from: ', client_address)
    
    # we receive the data from the client
    data = client_socket.recv(100)
    
    # we print what we got from him
    print('Received: ', data)

    # we send back the same data with CapsLk
    client_socket.send(data.upper())
    
    # we close the socket of the current client
    client_socket.close()
    
    # we print a 'disconnected' msg
    print('Client disconnected')