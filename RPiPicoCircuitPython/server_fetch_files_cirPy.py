import socketpool
import wifi
import re
import json
import os

# Connect to Wi-Fi
ssid = 'Ejemplo'
password = '12345678'

wifi.radio.connect(ssid, password)

print('Connected to Wi-Fi')
print('IP Address:', wifi.radio.ipv4_address)

# HTML content
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

    <script src="/files/script.js"></script>
</body>
</html>
"""

# JavaScript content (mimicking the content in the separate .js file)
script_js = """
function sendJson() {
    const jsonData = {
        key1: "value1",
        key2: "value2",
        key3: "value3"
    };

    const queryString = new URLSearchParams(jsonData).toString();

    fetch(`/api?${queryString}`)
        .then(response => response.json())  // Expect JSON response
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
}
"""

# Function to handle incoming requests
def handle_request(client):

    buffer = bytearray(1024)  # Create a mutable buffer
    bytes_received, address = client.recvfrom_into(buffer)  # Receive data into the buffer and get the sender's address
    request_str = str(buffer[:bytes_received])
    print("Received from:", address)
    print("Received data:", request_str)

    # Serve the HTML page
    if 'GET / ' in request_str or 'GET /index.html' in request_str:
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/html\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(html.encode('utf-8'))
    
    # Serve the JavaScript file
    elif 'GET /files/script.js' in request_str:
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: application/javascript\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(script_js.encode('utf-8'))

    # Handle the API request
    elif 'GET /api' in request_str:
        match = re.search(r'GET /api\?([^\s]+) HTTP', request_str)
        if match:
            query_string = match.group(1)
            params = query_string.split('&')
            json_data = {}
            for param in params:
                key, value = param.split('=')
                json_data[key] = value

            print("Received JSON data:")
            print(json.dumps(json_data))  # Pretty print the JSON data

        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/plain\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(json.dumps({"status": "success", "received_data": json_data}).encode('utf-8'))
    
    else:
        client.send("HTTP/1.1 404 Not Found\r\n")
        client.send("Content-Type: text/plain\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send("404 Not Found\r\n")

    client.close()

# Start the server
def start_server():
    pool = socketpool.SocketPool(wifi.radio)
    server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(1)

    print('Server listening on 0.0.0.0:80')

    while True:
        client, addr = server_socket.accept()
        print('Client connected from', addr)
        handle_request(client)

# Start the web server
start_server()


# Powered by ChatGPT