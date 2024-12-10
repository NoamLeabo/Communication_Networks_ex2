import socket
import os

# we create the socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# we bind the socket woth a specific port of '12345'
server.bind(('', 8888))

# we set the server to listen to at most 5 connections
server.listen(5)

# the endless loop of the server
while True:

    # we accept a 'connect' request that was sent to the server #
    # client_socket - the socket we are gonna communicate with from now on with the current client
    # client_address - the address of the client which we received a request from
    client_socket, client_address = server.accept()
    
    # we print who did we connect with
    print('Connection from: ', client_address) # TODO - REMOVE

    # a bool whether we move in to the next client
    next_client = False
    # we init a buffer to receive dynamic data from the client  
    buffer = ''

    # we connect to a specific client_socket as long as this is not the turn of 'next_client' yet
    while not next_client:
        # if the buffer is empty we try to do recv from the socket
        if len(buffer) == 0:
            # we try for no more then 1 sec
            client_socket.settimeout(100)
            try:
                # append data from the socket to the buffer
                buffer = client_socket.recv(1024).decode()
            # if the time has passed and we could't read we close the socket and move on to the next_client
            except socket.timeout:
                print('Socket timeout, closing connection')
                client_socket.close()
                next_client = True
                break
        
        # as long as we didn't reach to the end of the request from the client
        while '\r\n\r\n' not in buffer:
            # once again we try to append more data from the socket to the buffer
            client_socket.settimeout(100)
            try:
                buffer += client_socket.recv(1024).decode()
            # if the time has passed and we could't read we close the socket and move on to the next_client
            except socket.timeout:
                print('Socket timeout, closing connection')
                client_socket.close()
                next_client = True
                break
        
        # we check if we should break
        if next_client:
            break
        
        # we extract the data and save the rest as this is part of the next request
        data = buffer[:buffer.find('\r\n\r\n')]
        buffer = buffer[buffer.find('\r\n\r\n')+4:]

        # we print what we got from the client
        print('Received: ', data) # TODO - check format of HEMI

        # the first line of the data
        first_ln = data.split('\n')[0]
        # we split it to 3 parts according to http protocol
        action, req, protocol = first_ln.split(' ')
        # we extract from the header the status of the connection
        connection_status = [next(line for line in data.split(
            '\n') if line.startswith('Connection'))]

        # we check if we need to return the index.html
        if req == '/':
            # we try to construct the res to the client
            try:
                # we read the required file
                content = open(f'files/index.html', 'r').read()
                # save its length
                length = content.encode().__len__()
                # formatting the res
                res = f'HTTP/1.1 200 OK\n' \
                    f'Connection: {connection_status}\n' \
                    f'Content-length: {length}\n\n' \
                    f'{content}'
                # send the res back
                client_socket.send(res.encode())
                # if the status is 'close' we close the socket and move on to the next_client 
                if connection_status == "close":
                    client_socket.close()
                    next_client = True
                    break
            # if we got an error this is most probably because we couldn't read the file
            except Exception as err:
                # we return 404 file was not found, close the socket and move on to the next_client
                res = 'HTTP/1.1 404 Not Found\n' \
                      'Connection: close\n\n'
                client_socket.send(res.encode())
                client_socket.close()
                next_client = True
                break

        # we check if we need to return a jpg or ico file
        elif req.endswith(".ico") or req.endswith("jpg"):
            # we try to construct the res to the client
            try:
                # we read the required file as binary format
                content = open(f'files{req}', 'rb').read()
                # save its length
                length = content.__len__()
                # formatting the res
                res = f'HTTP/1.1 200 OK\n' \
                      f'Connection: {connection_status}\n' \
                      f'Content-length: {length}\n\n' 
                # send the first part of the res back
                client_socket.send(res.encode() + content) 
                # if the status is 'close' we close the socket and move on to the next_client
                if connection_status == "close":
                    client_socket.close()
                    next_client = True
                    break
            # if we got an error this is most probably because we couldn't read the file
            except Exception as err:
                # we return 404 file was not found, close the socket and move on to the next_client
                res = 'HTTP/1.1 404 Not Found\n' \
                      'Connection: close\n\n'
                client_socket.send(res.encode())
                client_socket.close()
                next_client = True
                break
        
        # we check if we need to return /redirect
        elif req == '/redirect':
            # formatting the res
            res = 'HTTP/1.1 301 Moved Permanently\n' \
                  'Connection: close\n' \
                  'Location: /result.html\n\n'
            # send the first part of the res back, close the socket and move on to the next_client
            client_socket.send(res.encode())
            client_socket.close()
            next_client = True

        # this is a generic request
        else:
            # we try to construct the res to the client
            try:
                # we read the required file
                content = open(f'files{req}', 'r').read()
                # save its length
                length = content.encode().__len__()
                # formatting the res
                res = f'HTTP/1.1 200 OK\n' \
                      f'Connection: {connection_status}\n' \
                      f'Content-length: {length}\n\n' \
                      f'{content}'
                # send the res back
                client_socket.send(res.encode())
                # if the status is 'close' we close the socket and move on to the next_client
                if connection_status == "close":
                    client_socket.close()
                    next_client = True
                    break
            # if we got an error this is most probably because we couldn't read the file
            except Exception as err:
                # we return 404 file was not found, close the socket and move on to the next_client
                res = 'HTTP/1.1 404 Not Found\n' \
                      'Connection: close\n\n'
                client_socket.send(res.encode())
                client_socket.close()
                next_client = True
                break

    # we print a 'disconnected' msg
    print('Client disconnected')