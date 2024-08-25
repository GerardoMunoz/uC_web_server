import socketpool
import wifi

URL_other='https://raw.githubusercontent.com'

wifi.radio.connect("Ejemplo","12345678")
pool=socketpool.SocketPool(wifi.radio)

print("wifi.radio",wifi.radio.hostname, wifi.radio.ipv4_address)
s = pool.socket()
s.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)
response = """
<!DOCTYPE html>
<html>
    <head>
        <title>My arm in three.js</title>
        <style>
            body { margin: 0; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/three@0.126.1/build/three.min.js"></script>
    </head>
    <body>
        <div id="arm"></div>
        <h1>ARM</h1>
        <div id="error"></div>

        <!-- Link to the external JavaScript file -->
        <script src="https://gerardomunoz.github.io/uC_web_server/RPiPicoCircuitPython/web_server_threejs/arm_three_js.js"></script>
    
    </body>
</html>
"""


while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  buffer = bytearray(1024)  # Create a mutable buffer
  bytes_received, address = conn.recvfrom_into(buffer)  # Receive data into the buffer and get the sender's address
  print("Received from:", address)
  print("Received data:", buffer[:bytes_received])
  conn.send('HTTP/1.1 200 OK\r\n')
  conn.send('Content-Type: text/html\r\n')
  conn.send(f'Access-Control-Allow-Origin: {URL_other}\r\n')
  conn.send('Access-Control-Allow-Credentials: true\r\n')
  conn.send('\r\n')
  conn.send(response)
  conn.close()