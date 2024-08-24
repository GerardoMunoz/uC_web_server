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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World</title>
</head>
<body>
    <h1 id="greeting"></h1>

    <!-- Link to the external JavaScript file -->
    <script src="https://gerardomunoz.github.io/uC_web_server/RPiPicoCircuitPython/web_server_jsfile/greeting.js"></script>
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