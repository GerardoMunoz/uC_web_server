import network
import socket
import ure
import json

# Connect to Wi-Fi
ssid = 'Ejemplo'
password = '12345678'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
while not wlan.isconnected():
    pass

print('Connected to Wi-Fi')
print(wlan.ifconfig())

# HTML content to serve
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send JSON via GET</title>
</head>
<body>
    <h1>Send JSON Data via GET Request</h1>
    <button onclick="sendJson()">Send JSON</button>

    <script>
        function sendJson() {
            const jsonData = {
                key1: "value1",
                key2: "value2",
                key3: "value3"
            };

            const queryString = new URLSearchParams(jsonData).toString();

            fetch(`/api?${queryString}`)
                .then(response => response.text())
                .then(data => console.log(data))
                .catch(error => console.error('Error:', error));
        }
    </script>
</body>
</html>
"""

# Function to handle incoming requests
def handle_request(client):
    request = client.recv(1024)
    request_str = request.decode('utf-8')
    
    print('Received request:')
    print(request_str)

    # Serve the HTML page
    if 'GET / ' in request_str or 'GET /api' not in request_str:
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/html\r\n')
        client.send('Connection: close\r\n\r\n')
        client.sendall(html)
    
    # Handle the API request
    elif 'GET /api' in request_str:
        match = ure.search(r'GET /api\?([^\s]+) HTTP', request_str)
        if match:
            query_string = match.group(1)
            params = query_string.split('&')
            json_data = {}
            for param in params:
                key, value = param.split('=')
                json_data[key] = value
            
            print("Received JSON data:")
            print(json.dumps(json_data))  # Pretty print the JSON data

        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send('Request received and processed\r\n')
    
    client.close()

# Start the server
def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    
    print('Server listening on', addr)
    
    while True:
        client, addr = server_socket.accept()
        print('Client connected from', addr)
        handle_request(client)

# Start the web server
start_server()

