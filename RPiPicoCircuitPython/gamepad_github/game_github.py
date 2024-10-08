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
html= """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joystick with Car Control</title>
    <link rel="stylesheet" href="https://gerardomunoz.github.io/uC_web_server/RPiPicoCircuitPython/gamepad_github/style.css">
    <!--link rel="stylesheet" href="http://192.168.65.1:8000/style.css"-->
</head>
<body>

<div id="buttonsContainer">
    <button class="button" id="btnUp">Up</button>
    <button class="button" id="btnDown">Down</button>
    <button class="button" id="btnLeft">Left</button>
    <button class="button" id="btnRight">Right</button>
</div>

<div id="joystickContainer">
    <div id="joystick"></div>
    <div id="coordinates">X: 75, Y: 75</div>
</div>

<div id="car"></div>
    <script src="https://gerardomunoz.github.io/uC_web_server/RPiPicoCircuitPython/gamepad_github/script.js"></script>
    <!--script src="http://192.168.65.1:8000/script.js"></script-->


</body>
</html>

"""

# html_dict={
# "style1":"""
#         body {
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#             height: 100vh;
#             margin: 0;
#             background-color: #f0f0f0;
#             font-family: Arial, sans-serif;
#         }
#         #buttonsContainer {
#             display: grid;
#             grid-template-columns: 1fr 1fr;
#             grid-gap: 20px;
#             margin-left: 50px;
#         }
#         .button {
#             width: 80px;
#             height: 80px;
#             background-color: #888;
#             border: none;
#             border-radius: 10px;
#             color: white;
#             font-size: 18px;
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             cursor: pointer;
#             user-select: none;
#         }
# """,
# "style2":"""
#        #joystickContainer {
#             width: 200px;
#             height: 200px;
#             background-color: #ddd;
#             border-radius: 50%;
#             position: relative;
#             touch-action: none;
#             margin-right: 50px;
#         }
#         #joystick {
#             width: 50px;
#             height: 50px;
#             background-color: #333;
#             border-radius: 50%;
#             position: absolute;
#             left: 75px;
#             top: 75px;
#         }
#         #coordinates {
#             text-align: center;
#             margin-top: 10px;
#             font-size: 18px;
#         }
#         #car {
#             position: absolute;
#             width: 100px;
#             height: 50px;
#             background-color: red;
#             border-radius: 10px;
#             left: 50%;
#             top: 50%;
#             transform: translate(-50%, -50%);
#         }
# """,
# 
# "script1":"""
#     const joystick = document.getElementById('joystick');
#     const joystickContainer = document.getElementById('joystickContainer');
#     const coordinatesDisplay = document.getElementById('coordinates');
#     const car = document.getElementById('car');
#     let lastX = 75, lastY = 75;
#     let carPosX = window.innerWidth / 2 - 50;
#     let carPosY = window.innerHeight / 2 - 25;
# 
#     function updateCarPosition(deltaX, deltaY) {
#         carPosX += deltaX;
#         carPosY += deltaY;
#         car.style.left = `${carPosX}px`;
#         car.style.top = `${carPosY}px`;
#     }
# 
# 
# """,
# 
# "script2":"""
# 
#     function getJoystickPosition(event) {
#         const rect = joystickContainer.getBoundingClientRect();
#         const offsetX = (event.touches ? event.touches[0].clientX : event.clientX) - rect.left;
#         const offsetY = (event.touches ? event.touches[0].clientY : event.clientY) - rect.top;
#         const x = Math.min(Math.max(offsetX - 25, 0), rect.width - 50);
#         const y = Math.min(Math.max(offsetY - 25, 0), rect.height - 50);
#         return { x, y };
#     }
# 
#     function updateJoystickPosition(event) {
#         const { x, y } = getJoystickPosition(event);
#         joystick.style.left = `${x}px`;
#         joystick.style.top = `${y}px`;
#         return { x, y };
#     }
# 
#     let currentPos = { x: 75, y: 75 };
# 
#     function handleMove(event) {
#         event.preventDefault();
#         currentPos = updateJoystickPosition(event);
#     }
# 
# 
#     function handleEnd() {
#         joystick.style.left = '75px';
#         joystick.style.top = '75px';
#         currentPos = { x: 75, y: 75 };
#     }
# 
# """,
# 
# "script3":"""
# 
#     
#     joystickContainer.addEventListener('mousedown', handleMove);
#     joystickContainer.addEventListener('mousemove', handleMove);
#     joystickContainer.addEventListener('mouseup', handleEnd);
#     joystickContainer.addEventListener('mouseleave', handleEnd);
#     joystickContainer.addEventListener('touchstart', handleMove);
#     joystickContainer.addEventListener('touchmove', handleMove);
#     joystickContainer.addEventListener('touchend', handleEnd);
# 
#     setInterval(() => {
#         if (lastX !== currentPos.x || lastY !== currentPos.y) {
#             coordinatesDisplay.textContent = `X: ${currentPos.x}, Y: ${currentPos.y}`;
#             updateCarPosition(currentPos.x - lastX, currentPos.y - lastY);
#             lastX = currentPos.x;
#             lastY = currentPos.y;
#         }
#     }, 500);
# 
#     document.getElementById('btnUp').addEventListener('click', () => updateCarPosition(0, -10));
#     document.getElementById('btnDown').addEventListener('click', () => updateCarPosition(0, 10));
#     document.getElementById('btnLeft').addEventListener('click', () => updateCarPosition(-10, 0));
#     document.getElementById('btnRight').addEventListener('click', () => updateCarPosition(10, 0));
# 
# """,
# 
# # HTML content
# "index" : """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Joystick with Car Control</title>
#     <link rel="stylesheet" href="/files/style1">
#     <link rel="stylesheet" href="/files/style2">
# </head>
# <body>
# 
# <div id="buttonsContainer">
#     <button class="button" id="btnUp">Up</button>
#     <button class="button" id="btnDown">Down</button>
#     <button class="button" id="btnLeft">Left</button>
#     <button class="button" id="btnRight">Right</button>
# </div>
# 
# <div id="joystickContainer">
#     <div id="joystick"></div>
#     <div id="coordinates">X: 75, Y: 75</div>
# </div>
# 
# <div id="car"></div>
#     <script src="/files/script1"></script>
#     <script src="/files/script2"></script>
# 
# </body>
# </html>
# 
# """
# }




# # JavaScript content (mimicking the content in the separate .js file)
# script_js = """
# function sendJson() {
#     const jsonData = {
#         key1: "value1",
#         key2: "value2",
#         key3: "value3"
#     };
# 
#     const queryString = new URLSearchParams(jsonData).toString();
# 
#     fetch(`/api?${queryString}`)
#         .then(response => response.json())  // Expect JSON response
#         .then(data => console.log(data))
#         .catch(error => console.error('Error:', error));
# }
# """

# Function to handle incoming requests
def handle_request(client):

    buffer = bytearray(1024)  # Create a mutable buffer
    bytes_received, address = client.recvfrom_into(buffer)  # Receive data into the buffer and get the sender's address
    request_str = str(buffer[:bytes_received])
    print("Received from:", address)
    print("Received data:", request_str)

    # Serve the HTML page
    if 'GET / ' in request_str or 'GET /index.html' in request_str or 'GET /gamepad.html' in request_str:
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/html\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(html)
    
    # Serve the JavaScript file
#     elif 'GET /files/script.js' in request_str:
#         client.send("HTTP/1.1 200 OK\r\n")
#         client.send("Content-Type: application/javascript\r\n")
#         client.send("Connection: close\r\n\r\n")
#         client.send(script_js.encode('utf-8'))
    elif 'GET /files/' in request_str:
        requested_file = request_str.split(' ')[1].split('/')[-1].strip()
        print('requested_file',requested_file)
        # Check if the requested file exists in the web_content dictionary
        if requested_file in html:
            content_type = "application/javascript" if "script" in requested_file else "text/css"
            client.send("HTTP/1.1 200 OK\r\n")
            client.send(f"Content-Type: {content_type}\r\n")
            client.send("Connection: close\r\n\r\n")
            client.send(html_dict[requested_file])
        else:
            client.send("HTTP/1.1 404 Not Found\r\n")
            client.send("Content-Type: text/plain\r\n")
            client.send("Connection: close\r\n\r\n")
            client.send("404 Not Found\r\n")

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
        print(request_str)
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
