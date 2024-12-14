import socket
import sys

# we get the server's port as an arg
server_Ip = sys.argv[1]

# we get the server's ip as an arg
server_Port = int(sys.argv[2])

# the endless loop of the server
while True:
    req = input()
    # we create a connection with the TCP server
    # we send teh word hello
    formatted_req = f'GET {req} HTTP/1.1\r\nConnection: close\r\n\r\n'
    # we extract the name of the file
    name_of_new_file = req.split('/')[-1]

    # we create the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_Ip, server_Port))
    s.send(formatted_req.encode())

    while True:
        # we wait to receive the data coming from the server
        data = s.recv(1024)
        # we wanna keep receiving bytes as long as we did not get the whole header which ends with '\r\n\r\n'
        while b'\r\n\r\n' not in data:
            try:
                data = s.recv(1024)
            finally:
                pass
        
        # we extract the first line from the response 
        first_ln = data.split(b'\r\n')[0].decode()
        # we print it as required
        print(first_ln)
        # we wanna check what type of msg we got back
        res_status = data[:12]

        # if this is an 'ok 200' we keep going and create the file
        if res_status == b'HTTP/1.1 200':
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
            while length_of_content > length_of_content_received:
                # we try to bring the delta (plus 10 for backup)
                try:
                    more_data = s.recv(length_of_content - length_of_content_received + 10)
                finally:
                    # if we acctually got something we append it
                    if more_data:
                        data += more_data
                        length_of_content_received += len(more_data)
                
            # we extract the full content from the final constructed msg
            _, _, content = data.partition(b'\r\n\r\n')
            # if thie is a regular file we create it by the given name and write the content into it
            if req != '/':
                with open(name_of_new_file, 'wb') as file:
                    file.write(content)
                    # we close the socket since it has been closed by the server
                    s.close()
                    break
            # if we got '/' we simply name the file as 'index.html'
            else:
                with open("index.html", 'wb') as file:
                    file.write(content)
                    # we close the socket since it has been closed by the server
                    s.close()
                    break

        elif res_status == b'HTTP/1.1 301':
            # we wanna know how much of the content itself we managed to receive
            header, _, content_received = data.partition(b'\r\n\r\n')
            # we seek for the new location
            Location_line = next(line for line in data.split(
                b'\n') if line.startswith(b'Location: '))
            # we extract the new location
            new_location = Location_line.split(b' ')[1]
            # we remove the '\r' suffix and docode it back to string
            new_location_separated = new_location.split(b'\r')[0].decode()
            # we format the new req with the new location
            formatted_req = f'GET {new_location_separated} HTTP/1.1\r\nConnection: close\r\n\r\n'
            # we extract the name of the new location file
            name_of_new_file = new_location_separated.split('/')[-1]
            # we close the current socket
            s.close()
            # then we create a new socket and reconnect to the server since the older one was closed by the server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_Ip, server_Port))
            # we send a new request to the new asked location
            s.send(formatted_req.encode())

        elif res_status == b'HTTP/1.1 404':
            # since the socket was closed we open a new one
            s.close()
            break
        
# we close the server (we never really get to there)
s.close()
