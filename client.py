import socket

# we create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8888))

# the endless loop of the server
while True:
    req = input()
    # we create a connection with the TCP server
    # we send teh word hello
    formatted_req = f'GET {req} HTTP/1.1\r\nConnection: keep-alive\r\n\r\n'
    s.send(formatted_req.encode())

    # we wait to receive the data coming from the server
    data = s.recv(1024)
    # we wanna keep receiving bytes as long as we did not get the whole header which ends with '\r\n\r\n'
    while b'\r\n\r\n' not in data:
        try:
            data = s.recv(1024)
        finally:
            pass
    
    # we wanna check what type of msg we got back
    first_ln = data[:15]

    # if this is an 'ok 200' we keep going and create the file
    if first_ln == b'HTTP/1.1 200 OK':
        # we wanna know how much of the content itself we managed to receive
        header, _, content_received = data.partition(b'\r\n\r\n')
        # the length of the content we managed to bring 
        length_of_content_received = len(content_received)
        # the length of the entire content we should be taking
        length_to_get = next(line for line in data.split(
            b'\n') if line.startswith(b'Content-length'))
        # we extract the number we should recv in byte type
        number_in_bytes = length_to_get.split(b' ')[1]
        # we convert the value of number_in_bytes to int after decoding it from byte type
        length_of_content = int(number_in_bytes.decode())
        # if the content we need to get is longer than what we took so far
        if length_of_content > length_of_content_received:
            # we try to bring the delta (plus 10 for backup)
            try:
                more_data = s.recv(length_of_content - length_of_content_received + 10)
            finally:
                # if we acctually got something we append it
                if more_data:
                    data += more_data
        
    # we extract the name of the file
    name_of_new_file = req.split('/')[-1]
    # we extract the full content from the final constructed msg
    _, _, content = data.partition(b'\r\n\r\n')
    # if thie is a regular file we create it by the given name and write the content into it
    if req != '/':
        with open(name_of_new_file, 'wb') as file:
            file.write(content)
    # if we got '/' we simply name the file as 'index.html'
    else:
        with open("index.html", 'wb') as file:
            file.write(content)

# we close the server (we never really get to there)
s.close()
