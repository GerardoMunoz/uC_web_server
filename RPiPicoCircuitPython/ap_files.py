import socketpool
import wifi
import os  # Assuming a filesystem is available

# Start the server
def start_server(ap=True):
    if ap:
        wifi.radio.start_ap("RPi-Pico", "12345678")
        print("wifi.radio ap:", wifi.radio.ipv4_address_ap)
    else:    
        wifi.radio.connect("Ejemplo","12345678")
        print("wifi.radio:",wifi.radio.hostname, wifi.radio.ipv4_address)
        
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

# Serve files requested by the client
def handle_request(client):
    buffer = bytearray(1024)  # Create a mutable buffer
    bytes_received, address = client.recvfrom_into(buffer)  # Receive data into the buffer and get the sender's address
    request = buffer[:bytes_received]
    #request = client.recv(1024)
    request_str = request.decode('utf-8')
    #print('Received request:',request_str)

    # Extract the requested file from the request
    try:
        request_file = request_str.split(' ')[1]
        print('request_file',request_file)
        if request_file == '/':
            request_file = '/index.html'  # Default to index.html if no file is requested
    except IndexError:
        client.send('HTTP/1.1 400 Bad Request\r\n')
        client.close()
        return

    # Construct the full file path you can adjust this to match your file structure)
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
                #print('chunk',chunk)
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
s = start_server(ap=False)
while True:
    conn, addr = s.accept()
    print(f'Got a connection from {addr}')
    handle_request(conn)