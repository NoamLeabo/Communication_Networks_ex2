import socket

# we create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# the endless loop of the server
while True:
    req = input()
    # we create a connection with the TCP server
    s.connect(('127.0.0.1', 8238))
    # we send teh word hello
    formatted_req = f'GET {req} HTTP/1.1\nConnection: close\r\n\r\n'
    s.send(formatted_req.encode())

    # we wait to receive the data coming from the server
    data = s.recv(1024)
    data += s.recv(10000)
    data = data.decode(errors="ignore")
    name_of_new_file = req.split('/')[-1]
    data = data[data.find('\n\n')+2:]
    data = data.encode(errors="ignore")
    with open(name_of_new_file, 'wb') as file:
        file.write(data)

    # we close the server
s.close()
