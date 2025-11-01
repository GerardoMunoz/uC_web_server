# main.py -- MicroPython para Raspberry Pi Pico W
import network
import socket
import time
import ubinascii
import hashlib
import struct
from ov7670_wrapper import *
from machine import Pin, I2C, SPI, PWM
import sys
import gc


# --- PARÁMETROS DE PINES (CÁMARA OV7670) ---
mclk_pin_no     = 22
pclk_pin_no     = 21
data_pin_base   = 2   # D0-D7: GP2 a GP9
vsync_pin_no    = 17
href_pin_no     = 26
reset_pin_no    = 14
shutdown_pin_no = 15
sda_pin_no      = 12
scl_pin_no      = 13


# ---------- 1) GENERAR XCLK CON PWM PARA LA CÁMARA ----------
print("Configurando MCLK para OV7670 en GP22...")
pwm = PWM(Pin(mclk_pin_no))
pwm.freq(30_000_000)
pwm.duty_u16(32768)

# ---------- 2) INICIALIZAR I2C y OV7670 ----------
print("Inicializando I2C y OV7670...")
i2c = I2C(0, freq=400_000, scl=Pin(scl_pin_no), sda=Pin(sda_pin_no))

try:
    ov7670 = OV7670Wrapper(
        i2c_bus=i2c,
        mclk_pin_no=mclk_pin_no,
        pclk_pin_no=pclk_pin_no,
        data_pin_base=data_pin_base,
        vsync_pin_no=vsync_pin_no,
        href_pin_no=href_pin_no,
        reset_pin_no=reset_pin_no,
        shutdown_pin_no=shutdown_pin_no,
    )
    ov7670.wrapper_configure_rgb()
    ov7670.wrapper_configure_base()

    width, height = ov7670.wrapper_configure_size(OV7670_WRAPPER_SIZE_DIV4)
    ov7670.wrapper_configure_test_pattern(OV7670_WRAPPER_TEST_PATTERN_NONE)
    print(f"✅ OV7670 inicializada. Resolución: {width}x{height}")
    frame_buf = bytearray(width * height * 2)
    gc.collect()

except Exception as e:
    print(f"❌ Error al inicializar la cámara OV7670: {e}")
    sys.exit(1)


# CONFIG ------------------------------------------------
SSID = "Ejemplo"
PASSWORD = "12345678"
HOST = "0.0.0.0"        # "" para escuchar en todas las interfaces
HTTP_PORT = 80
WS_PORT = 80     # usaremos el mismo socket HTTP y upgrade a /ws
WIDTH = 160
HEIGHT = 120
BUFSZ = WIDTH * HEIGHT *2  # 2*20800
SEND_INTERVAL = 1.0     # segundos entre envíos
# -------------------------------------------------------

GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

# Conectar a WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Conectando a WiFi...")
    wlan.connect(SSID, PASSWORD)
    timeout = time.time() + 15
    while not wlan.isconnected():
        if time.time() > timeout:
            raise RuntimeError("No se pudo conectar a WiFi")
        time.sleep(0.5)
print("Conectado, IP:", wlan.ifconfig()[0])

# Genera buffer de ejemplo: columnas de color
def make_column_image():
    # Un byte por pixel: cada columna tiene valor distinto
    buf = bytearray(BUFSZ)
#     for x in range(WIDTH):
#         v = int(x * 255 / (WIDTH - 1))
#         for y in range(HEIGHT):
#             buf[y * WIDTH + x] = v
    ov7670.capture(buf)
    return buf


# Responder HTTP básico (sirve la página y los recursos)
HTML_PAGE = """HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Connection: close

<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Pico W - WebSocket Image (130x160)</title>
  <style>
    body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:1rem}
    canvas{image-rendering:pixelated;border:1px solid #444}
  </style>
</head>
<body>
  <h3>Pico W — Stream WebSocket 160×120</h3>
  <canvas id="c" width="160" height="120" style="width:260px;height:320px;"></canvas>
  <p id="status">Conectando WebSocket...</p>
  <script>
  const W = 160, H = 120;
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  const status = document.getElementById('status');

  function hsvToRgb(h, s, v) {
    let c = v * s;
    let x = c * (1 - Math.abs((h / 60) % 2 - 1));
    let m = v - c;
    let r=0,g=0,b=0;
    if (0<=h && h<60){ r=c; g=x; b=0; }
    else if (60<=h && h<120){ r=x; g=c; b=0; }
    else if (120<=h && h<180){ r=0; g=c; b=x; }
    else if (180<=h && h<240){ r=0; g=x; b=c; }
    else if (240<=h && h<300){ r=x; g=0; b=c; }
    else { r=c; g=0; b=x; }
    return [Math.round((r+m)*255), Math.round((g+m)*255), Math.round((b+m)*255)];
  }

  function byteToRGB(byte) {
    // mapeo: byte(0..255) -> hue 0..360, s=1, v=1
    const hue = (byte / 255) * 360;
    return hsvToRgb(hue, 1, 1);
  }

  function renderFromBuffer(buf) {
    // buf: Uint8Array de W*H bytes
    const imgData = new Uint8Array(buf);
    const id = ctx.createImageData(W, H);
    const data = id.data;
//    for (let i=0; i < buf.length; i++){
//      const b = buf[i];
//      const [r,g,bl] = byteToRGB(b);
//      const idx = i * 4;
//      data[idx] = r;
//      data[idx+1] = g;
//      data[idx+2] = bl;
//      data[idx+3] = 255;
//    }
    
    for (let i = 0; i < imgData.length; i += 2) {
        if (i==imgData.length/2){
            
        }
        const rgb565 = (imgData[i] << 8) | imgData[i + 1];
        const r = ((rgb565 >> 11) & 0x1F) * 8;
        const g = ((rgb565 >> 5) & 0x3F) * 4;
        const b = (rgb565 & 0x1F) * 8;
        const index = (i / 2) * 4;
        data[index] = r;
        data[index + 1] = g;
        data[index + 2] = b;
        data[index + 3] = 255; // Alpha
        if (i==imgData.length/2){
            console.log('rgb565',rgb565,r,g,b)    
        }

    }
    ctx.putImageData(id, 0, 0);
    
    
  }

  // Conectar al WebSocket en la misma host
  const proto = (location.protocol === "https:") ? "wss://" : "ws://";
  const wsUrl = proto + location.host + "/ws";
  const ws = new WebSocket(wsUrl);
  ws.binaryType = "arraybuffer";

  ws.onopen = () => { status.textContent = "WebSocket abierto"; };
  ws.onclose = () => { status.textContent = "Desconectado"; };
  ws.onerror = (e) => { status.textContent = "Error WebSocket"; console.log(e); };

  ws.onmessage = (ev) => {
    const ab = ev.data;
    const u8 = new Uint8Array(ab);
    if (u8.length === W*H*2) {
      renderFromBuffer(u8);
    } else {
      console.log("Tamano recibido:", u8.length);
    }
  };
  </script>
</body>
</html>
"""








# Encabezado de respuesta cuando no es el websocket
def http_response_page():
    return HTML_PAGE

# Construye la respuesta handshake del WebSocket
def ws_handshake(key):
    accept_raw = hashlib.sha1(key + GUID).digest()
    accept_b64 = ubinascii.b2a_base64(accept_raw).strip()
    resp = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Accept: " + accept_b64.decode() + "\r\n\r\n"
    )
    return resp

# Enviar frame binario WebSocket sin máscara (servidor->cliente no enmascara)
def ws_send_binary(client_sock, payload):
    L = len(payload)
    # primer byte: FIN + opcode 2 (binario) -> 0x82
    print('payload',L)
    header = bytearray()
    header.append(0x82)
    if L <= 125:
        header.append(L)
    elif L <= 0xFFFF:
        header.append(126)
        header.extend(struct.pack(">H", L))
    else:
        header.append(127)
        header.extend(struct.pack(">Q", L))
    try:
        client_sock.send(header)
        # En MicroPython socket.send puede requerir loop para enviar todo
        sent = 0
        while sent < L:
            sent += client_sock.send(payload[sent:])
    except Exception as e:
        print("Error enviando frame:", e)
        raise

# Socket principal (sirve HTTP y puede hacer upgrade a WS en /ws)
print('socket',socket.getaddrinfo(HOST, HTTP_PORT))
addr = socket.getaddrinfo(HOST, HTTP_PORT)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
s.settimeout(None)
print("Servidor HTTP/WebSocket escuchando en", addr)

try:
    while True:
        cl, remote = s.accept()
        print("Conexión desde", remote)
        try:
            cl_file = cl.makefile("rwb", 0)
            # Leer request headers
            request_line = cl_file.readline()
            if not request_line:
                cl.close()
                continue
            headers = {}
            # request_line ejemplo: b"GET / HTTP/1.1\r\n"
            path = request_line.split()[1].decode()
            # leer headers hasta línea vacía
            while True:
                line = cl_file.readline()
                if not line or line == b"\r\n":
                    break
                parts = line.decode().split(":", 1)
                if len(parts) == 2:
                    headers[parts[0].strip().lower()] = parts[1].strip()
            # Si es upgrade a websocket y path == /ws -> handshake
            if headers.get("upgrade", "").lower() == "websocket" and path == "/ws":
                key_b64 = headers.get("sec-websocket-key", "")
                if not key_b64:
                    print("No Sec-WebSocket-Key")
                    cl.close()
                    continue
                key = key_b64.encode()
                resp = ws_handshake(key)
                cl.send(resp.encode())
                print("Handshake WebSocket OK, enviando frames...")

                # Enviar imagenes periódicamente
                try:
                    while True:
                        buf = make_column_image()  # si deseás, podrías reemplazar por el buffer real
                        ws_send_binary(cl, buf)
                        time.sleep(SEND_INTERVAL)
                except Exception as e:
                    print("Cliente WS desconectado o error:", e)
                finally:
                    cl.close()
            else:
                # Servir página HTML (GET /)
                page = http_response_page()
                cl.send(page.encode())
                cl.close()
        except Exception as e:
            print("Error en conexión:", e)
            try:
                cl.close()
            except:
                pass

except KeyboardInterrupt:
    s.close()
    print("Servidor cerrado")
    
    
