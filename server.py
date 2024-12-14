import socket
import os
import sys

# we get the port where the server runs as an arg
Port = int(sys.argv[1])
# we create the socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# we bind the socket woth a specific port of '12345'
server.bind(('', Port))

# we set the server to listen to at most 5 connections
server.listen(5)

# the endless loop of the server
while True:

    # we accept a 'connect' request that was sent to the server #
    # client_socket - the socket we are gonna communicate with from now on with the current client
    # client_address - the address of the client which we received a request from
    client_socket, client_address = server.accept()
    
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
                if not len(buffer):
                    client_socket.close()
                    break
            # if the time has passed and we could't read we close the socket and move on to the next_client
            except socket.timeout:
                # print('Socket timeout, closing connection')
                client_socket.close()
                break
        
        # as long as we didn't reach to the end of the request from the client
        while '\r\n\r\n' not in buffer:
            # once again we try to append more data from the socket to the buffer
            client_socket.settimeout(100)
            try:
                try_to_get_more = client_socket.recv(1024).decode()
                buffer += try_to_get_more
                if not len(try_to_get_more):
                    client_socket.close()
                    break
            # if the time has passed and we could't read we close the socket and move on to the next_client
            except socket.timeout:
                # print('Socket timeout, closing connection')
                client_socket.close()
                next_client = True
                break
        
        # we check if we should break
        if next_client:
            break
        
        # we extract the data and save the rest as this is part of the next request
        data = buffer[:buffer.find('\r\n\r\n') + 4]
        buffer = buffer[buffer.find('\r\n\r\n') + 4:]

        # we print what we got from the client
        print(data)

        # the first line of the data
        first_ln = data.split('\r\n')[0]
        # we split it to 3 parts according to http protocol
        action, req, protocol = first_ln.split(' ')
        # we extract from the header the status of the connection
        connection_status = next(line for line in data.split(
            '\r\n') if line.startswith('Connection'))
        # we extract the actual value of 'Connection' field
        stat = connection_status.split(' ')[-1]

        # we wanna check if the path is valid and is a file before trying to open it
        if not os.path.isfile(f'files{req}') and os.path.normpath(req) != os.path.normpath('/redirect'):
            res = 'HTTP/1.1 404 Not Found\r\n' \
                'Connection: close\r\n\r\n'
            client_socket.send(res.encode())
            client_socket.close()
            next_client = True
            break

        # we wanna do a conversion to the path to make it adaptive to all os
        req = os.path.normpath(f'files{req}')
        
        # we check if we need to return the index.html
        if req == os.path.normpath('files/'):
            # we try to construct the res to the client
            try:
                # we read the required file
                content = open(os.path.normpath('files/index.html'), 'r').read()
                # save its length
                length = content.encode().__len__()
                # formatting the res
                res = f'HTTP/1.1 200 OK\r\n' \
                    f'Connection: {stat}\r\n' \
                    f'Content-length: {length}\r\n\r\n' \
                    f'{content}'
                # send the res back
                client_socket.send(res.encode())
                # if the status is 'close' we close the socket and move on to the next_client 
                if stat == "close":
                    client_socket.close()
                    next_client = True
                    break
            # if we got an error this is most probably because we couldn't read the file
            except Exception as err:
                # we return 404 file was not found, close the socket and move on to the next_client
                res = 'HTTP/1.1 404 Not Found\r\n' \
                      'Connection: close\r\n\r\n'
                client_socket.send(res.encode())
                client_socket.close()
                next_client = True
                break

        # we check if we need to return a jpg or ico file
        elif req.endswith(".ico") or req.endswith(".jpg"):
            # we try to construct the res to the client
            try:
                # we read the required file as binary format
                content = open(req, 'rb').read()
                # save its length
                length = content.__len__()
                # formatting the res
                res = f'HTTP/1.1 200 OK\r\n' \
                    f'Connection: {stat}\r\n' \
                      f'Content-length: {length}\r\n\r\n' 
                # send the first part of the res back
                client_socket.send(res.encode() + content) 
                # if the status is 'close' we close the socket and move on to the next_client
                if stat == "close":
                    client_socket.close()
                    next_client = True
                    break
            # if we got an error this is most probably because we couldn't read the file
            except Exception as err:
                # we return 404 file was not found, close the socket and move on to the next_client
                res = 'HTTP/1.1 404 Not Found\r\n' \
                      'Connection: close\r\n\r\n'
                client_socket.send(res.encode())
                client_socket.close()
                next_client = True
                break
        
        # we check if we need to return /redirect
        elif req == os.path.normpath('files/redirect'):
            # formatting the res
            res = 'HTTP/1.1 301 Moved Permanently\r\n' \
                  'Connection: close\r\n' \
                  'Location: /result.html\r\n\r\n'
            # send the first part of the res back, close the socket and move on to the next_client
            client_socket.send(res.encode())
            client_socket.close()
            next_client = True
            break

        # this is a generic request
        else:
            # we try to construct the res to the client
            try:
                # we read the required file
                content = open(req, 'r').read()
                # save its length
                length = content.encode().__len__()
                # formatting the res
                res = f'HTTP/1.1 200 OK\r\n' \
                    f'Connection: {stat}\r\n' \
                      f'Content-length: {length}\r\n\r\n' \
                      f'{content}'
                # send the res back
                client_socket.send(res.encode())
                # if the status is 'close' we close the socket and move on to the next_client
                if stat == "close":
                    client_socket.close()
                    next_client = True
                    break
            # if we got an error this is most probably because we couldn't read the file
            except Exception as err:
                # we return 404 file was not found, close the socket and move on to the next_client
                res = 'HTTP/1.1 404 Not Found\r\n' \
                      'Connection: close\r\n\r\n'
                client_socket.send(res.encode())
                client_socket.close()
                next_client = True
                break

    # we print a 'disconnected' msg
    # print('Client disconnected')