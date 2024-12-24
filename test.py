import socket
import threading
import time
import os


def send_request(ip, port, request):
    """
    Utility function to send a single request to the server and return the response.
    Handles socket creation, sending data, and receiving the full response.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.send(request.encode())
        response = b""
        while True:
            data = s.recv(1024)
            if not data:
                break  # Exit loop if no more data is received
            response += data
        return response.decode()
    except Exception as e:
        return f"Error: {e}"
    finally:
        s.close()  # Ensure socket is closed after the request


def test_basic_connection():
    """Test basic server connection and retrieval of index.html"""
    print("Test 1: Basic Connection")
    response = send_request(
        "127.0.0.1", 8888, "GET / HTTP/1.1\r\nConnection: close\r\n\r\n")
    assert "200 OK" in response, "Failed Basic Connection Test"
    print("Passed\n")


def test_Big_header():
    """Test test_Big_header server connection and retrieval of index.html"""
    print("Test 1.5: test Big header")
    garbeg = 'a'*10000
    response = send_request(
        "127.0.0.1", 8888, f"GET / HTTP/1.1\r\nX: {garbeg}\r\nConnection: close\r\n\r\n")
    assert "200 OK" in response, "Failed Basic Connection Test"
    print("Passed\n")


def test_file_not_found():
    """Test server response for a non-existent file"""
    print("Test 2: File Not Found")
    response = send_request(
        "127.0.0.1", 8888, "GET /nonexistent.txt HTTP/1.1\r\nConnection: close\r\n\r\n")
    assert "404 Not Found" in response, "Failed File Not Found Test"
    print("Passed\n")


def test_file_retrieval():
    """Test retrieval of a specific file from the server"""
    print("Test 3: File Retrieval")
    with open("files/test_file.txt", "w") as f:
        f.write("Hello, test!")  # Prepare the test file
    response = send_request(
        "127.0.0.1", 8888, "GET /test_file.txt HTTP/1.1\r\nConnection: close\r\n\r\n")
    assert "200 OK" in response and "Hello, test!" in response, "Failed File Retrieval Test"
    print("Passed\n")


def test_redirect():
    """Test server's handling of a redirect request"""
    print("Test 4: Redirect")
    response = send_request(
        "127.0.0.1", 8888, "GET /redirect HTTP/1.1\r\nConnection: close\r\n\r\n")
    assert "301 Moved Permanently" in response, "Failed Redirect Test"
    assert "Location: /result.html" in response, "Missing Location header in Redirect"
    print("Passed\n")


def test_large_file():
    """Test retrieval of a large file to ensure correct Content-Length and data transfer"""
    print("Test 5: Large File Retrieval")
    with open("files/large.txt", "w") as f:
        f.write("A" * 1024 * 1024)  # Create a 1MB test file
    response = send_request(
        "127.0.0.1", 8888, "GET /large.txt HTTP/1.1\r\nConnection: close\r\n\r\n")
    assert "200 OK" in response, "Failed Large File Retrieval Test"
    assert "Content-Length: 1048576" in response, "Incorrect Content-Length for Large File"
    print("Passed\n")


def test_binary_file():
    """Test retrieval of a binary file (e.g., image)"""
    print("Test 6: Binary File Retrieval")
    with open("files/image.jpg", "wb") as f:
        f.write(os.urandom(1024))  # Create a 1KB random binary file
    response = send_request(
        "127.0.0.1", 8888, "GET /image.jpg HTTP/1.1\r\nConnection: close\r\n\r\n")
    print(response)
    assert "200 OK" in response, "Failed Binary File Retrieval Test"
    print("Passed\n")


def test_malformed_request():
    """Test server's response to a malformed HTTP request"""
    print("Test 7: Malformed Request")
    response = send_request("127.0.0.1", 8888, "INVALID / HTTP/1.1\r\n\r\n")
    assert "400 Bad Request" in response, "Failed Malformed Request Test"
    print("Passed\n")


def test_keep_alive():
    """Test server's handling of persistent (keep-alive) connections"""
    print("Test 8: Keep-Alive Connection")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("127.0.0.1", 8888))
        request = "GET / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n"
        s.send(request.encode())
        response = s.recv(1024).decode()
        assert "200 OK" in response, "Failed Keep-Alive Test"
        # Send a second request without reconnecting
        s.send(request.encode())
        response2 = s.recv(1024).decode()
        assert "200 OK" in response2, "Failed Keep-Alive Second Request"
        print("Passed\n")
    finally:
        s.close()


def test_multiple_clients():
    """Stress test: Simulate multiple concurrent clients"""
    print("Test 9: Multiple Clients")

    def client():
        send_request("127.0.0.1", 8888,
                     "GET / HTTP/1.1\r\nConnection: close\r\n\r\n")

    threads = []
    for _ in range(25):  # Launch 25 concurrent clients
        t = threading.Thread(target=client)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()  # Wait for all threads to complete

    print("Passed\n")


def test_empty_request():
    """Test server response to an empty request"""
    print("Test 10: Empty Request")
    response = send_request("127.0.0.1", 8888, "")
    assert "400 Bad Request" in response, "Failed Empty Request Test"
    print("Passed\n")


def test_incomplete_request():
    """Test server response to an incomplete HTTP request"""
    print("Test 11: Incomplete Request")
    response = send_request(
        "127.0.0.1", 8888, "GET / HTTP/1.1\r\nConnection: close")
    assert "400 Bad Request" in response, "Failed Incomplete Request Test"
    print("Passed\n")


def test_multiple_large_files():
    """Test retrieval of multiple large files concurrently"""
    print("Test 12: Multiple Large Files")

    def client(file_name):
        send_request("127.0.0.1", 8888,
                     f"GET /{file_name} HTTP/1.1\r\nConnection: close\r\n\r\n")

    # Prepare large files
    for i in range(5):
        with open(f"files/large{i}.txt", "w") as f:
            f.write("A" * 1024 * 1024)

    threads = []
    for i in range(5):
        t = threading.Thread(target=client, args=(f"large{i}.txt",))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Passed\n")


def run_all_tests():
    """Run all tests sequentially"""
    print("Running Tests...\n")
    test_basic_connection()
    test_Big_header()
    test_file_not_found()
    test_file_retrieval()
    test_redirect()
    test_large_file()
    # test_binary_file()
    # test_malformed_request()
    test_keep_alive()
    test_multiple_clients()
    # test_empty_request()
    # test_incomplete_request()
    test_multiple_large_files()
    print("All Tests Passed Successfully!\n")


if __name__ == "__main__":
    run_all_tests()
