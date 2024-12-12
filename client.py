import socket

# we create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8888))

# the endless loop of the server
while True:
    req = input()
    # we create a connection with the TCP server
    # we send teh word hello
    formatted_req = f'GET {req} HTTP/1.1\nConnection: close\r\n\r\n'
    s.send(formatted_req.encode())

    # we wait to receive the data coming from the server
    data = s.recv(1024)
    t = data[:16]
    if data[:15] == b'HTTP/1.1 200 OK':
        while b'Content-length: ' not in data:
            data += s.recv(1024)
        length_to_get = next(line for line in data.split(
            b'\n') if line.startswith(b'Content-length'))
        res = length_to_get.split(b' ')[1]
        num = int(res.decode())
        data += s.recv(num)
    name_of_new_file = req.split('/')[-1]
    _, _, data = data.partition(b'\n\n')
    with open(name_of_new_file, 'wb') as file:
        file.write(data)

    # we close the server
s.close()
