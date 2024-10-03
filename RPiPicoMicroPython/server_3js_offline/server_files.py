import os  # Assuming a filesystem is available
import time
# Start the server
def start_server(ap=True):
#     try:
#         import network
#         import socket
#         if ap:
#             wifi.radio.start_ap("RPi-Pico", "12345678")
#             print("wifi.radio ap:", wifi.radio.ipv4_address_ap)
#         else:
#             
#             wifi.radio.connect("Ejemplo","12345678")
#             print("wifi.radio:",wifi.radio.hostname, wifi.radio.ipv4_address)
#         pool = socketpool.SocketPool(wifi.radio)
#         s = pool.socket()
#     except:
    import network
    import socket
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("Ejemplo","12345678")
    print('Connected to Wi-Fi',wlan.ifconfig())
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
        
    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
    #addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    #print('Server listening on', addr)
    s = socket.socket()
        
   
    

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

def html_line_generator(file_path, max_length=1200):
    """
    This function reads lines from an HTML file and yields parts of the HTML that are 
    less than or equal to a specified character limit (default is 1200 characters). 
    If a line exceeds the limit, it breaks the line into smaller parts and yields them.
    """
    with open(file_path, 'r') as html_file:
        buffer = ""
        
        for line in html_file:
            buffer += line
            
            while len(buffer) > max_length:
                yield buffer[:max_length]
                buffer = buffer[max_length:]
                
            if len(buffer) <= max_length:
                yield buffer
                buffer = ""
                
        if buffer:
            yield buffer



# Serve files requested by the client
def handle_request(client):
    #buffer = bytearray(1024)  # Create a mutable buffer
    #print(type(client))
    #bytes_received, address = client.recvfrom_into(buffer)  # Receive data into the buffer and get the sender's address
    #request = buffer[:bytes_received]
    request, address = client.recvfrom(1024)  # Receive data into the buffer and get the sender's address

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

        # Example usage in the server response part.
        #html_file_path = 'path/to/your/file.html'

        for html_part in html_line_generator(file_path):
            #print(html_part)
            print('.',end='')
            client.send(html_part)
            time.sleep_ms(100)
        #client.close()



#         # Send the file content in chunks
#         with open(file_path, 'rb') as file:
#             while True:
#                 chunk = file.read(1024)
#                 #print('chunk',chunk)
#                 if not chunk:
#                     break
#                 client.send(chunk)
#                 time.sleep_ms(100)
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