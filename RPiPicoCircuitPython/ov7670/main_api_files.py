import socketpool
import wifi
import os  # Assuming a filesystem is available

# Import the API method from the separate file
from api import api

# Start the server
def start_server(ap=True):
    if ap:
        wifi.radio.start_ap("RPi-Pico", "12345678")
        print("wifi.radio ap:", wifi.radio.ipv4_address_ap)
    else:    
        wifi.radio.connect("Ejemplo","12345678")
        print("wifi.radio:", wifi.radio.ipv4_address)
        
    pool = socketpool.SocketPool(wifi.radio)
    
    s = pool.socket()
    s.bind(('', 80))
    s.listen(5)
    return s

# Get the correct content type based on file extension
def get_content_type(filename):
    if filename.endswith('.html'):
        return 'text/html'
    elif filename.endswith('.js'):
        return 'application/javascript'
    elif filename.endswith('.css'):
        return 'text/css'
    elif filename.endswith('.png'):
        return 'image/png'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        return 'image/jpeg'
    elif filename.endswith('.gif'):
        return 'image/gif'
    else:
        return 'application/octet-stream'

# Check if file exists using os.listdir()
def file_exists(filename):
    directory = '.'  # Directory where the files are stored
    files = os.listdir(directory)  # List all files in the directory
    return filename.lstrip('/') in files

# Serve files or handle API requests
def handle_request(client):
    buffer = bytearray(1024)  # Create a mutable buffer
    bytes_received, address = client.recvfrom_into(buffer)  # Receive data into the buffer and get the sender's address
    request = buffer[:bytes_received]
    request_str = request.decode('utf-8')

    # Extract the requested file from the request
    try:
        request_file = request_str.split(' ')[1]
        print('request_file', request_file)
        if request_file == '/':
            request_file = '/index.html'  # Default to index.html if no file is requested
    except IndexError:
        client.send('HTTP/1.1 400 Bad Request\r\n')
        client.close()
        return

    # Check if the request is for the API endpoint
    if request_file.startswith('/api'):
        # Call the api() method from api.py
        response = api( request_str)
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: application/octet-stream\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(response)
        client.close()
        return

    # Construct the full file path (you can adjust this to match your file structure)
    file_path = '.' + request_file  # Assuming files are in the current directory

    # Check if the file exists
    if file_exists(request_file):
        print('file_exists')
        # Get the content type for the requested file
        content_type = get_content_type(file_path)

        # Send headers
        client.send('HTTP/1.1 200 OK\r\n')
        client.send(f'Content-Type: {content_type}\r\n')
        client.send('Connection: close\r\n\r\n')

        # Send the file content in chunks
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                client.send(chunk)
    else:
        print('file does not exist')
        # Send 404 Not Found response
        client.send('HTTP/1.1 404 Not Found\r\n')
        client.send('Content-Type: text/html\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send('<h1>404 Not Found</h1>')

    client.close()

# Start the server and listen for connections
s = start_server(ap=True)
while True:
    conn, addr = s.accept()
    print(f'Got a connection from {addr}')
    handle_request(conn)
