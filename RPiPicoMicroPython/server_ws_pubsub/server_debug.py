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
########################

formatos={
    "STR":0x1,
    "JSON":0x2,
    "RGB565":0x3
    }


###########################################

import re
import _thread

class MessageBus:
    def __init__(self,queues=[]):
        self.subscribers = {}
        self.lock = _thread.allocate_lock()
        self.queues=queues

    def subscribe(self, topic, callback):
        with self.lock:
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            self.subscribers[topic].append(callback)

    def publish(self, topic, message):
        with self.lock:
            callbacks = list(self.subscribers.get(topic, []))
        topic_b = topic.encode()
        header = bytes([0x00, len(topic_b)]) + topic_b
        frame = header + message
        outbox.push(frame)
        print('publish',topic,len(frame))
        for cb in callbacks:
            try:
                #print('publish',0)
                cb(topic, message)
            except Exception as e:
                print("Error en callback", topic, e)

# class MessageBus:
#     def __init__(self):
#         self.subscribers = []  # lista de (regex, callback, topic_pattern)
#         self.lock = _thread.allocate_lock()
# 
#     def _topic_to_regex(self, topic_pattern):
#         """
#         Convierte un patrón tipo 'sensor/+/temp' o 'sensor/#'
#         a una expresión regular.
#         """
#         # Escapar puntos y caracteres especiales de regex
#         regex = re.escape(topic_pattern)
#         # Reemplazar MQTT wildcards por regex equivalentes
#         regex = regex.replace(r'\+', r'[^/]+')   # un nivel
#         regex = regex.replace(r'\#', r'.*')      # todos los niveles
#         # Debe coincidir toda la cadena
#         regex = '^' + regex + '$'
#         return re.compile(regex)
# 
#     def subscribe(self, topic_pattern, callback):
#         with self.lock:
#             regex = self._topic_to_regex(topic_pattern)
#             self.subscribers.append((regex, callback, topic_pattern))
# 
#     def publish(self, topic, message):
#         with self.lock:
#             handlers = [(cb, pat) for (rx, cb, pat) in self.subscribers if rx.match(topic)]
#         for cb, pat in handlers:
#             try:
#                 cb(topic, message)
#             except Exception as e:
#                 print(f"Error en callback ({pat}):", e)
# 


# def handler(topic, msg):
#     print(f"[{topic}] → {msg}")


# bus.subscribe("sensor/+/temp", handler)
# bus.subscribe("sensor/#", handler)
# 
# bus.publish("sensor/living/temp", "22°C")  # Coincide con ambos
# bus.publish("sensor/outdoor/humidity", "80%")  # Solo con sensor/#


class ThreadSafeQueue:
    def __init__(self):
        self.q = []
        self.lock = _thread.allocate_lock()

    def push(self, item):
        #print('push',len(self.q),end=' ')
        with self.lock:
            self.q.append(item)

    def pop(self):
        #print('pop',len(self.q),end=' ')
        with self.lock:
            if self.q:
                #print('pop',len(self.q),end=' ')
                return self.q.pop(0)
            else:
                return None

    def empty(self):
        with self.lock:
            return len(self.q) == 0
outbox = ThreadSafeQueue()

# def on_publish(topic, payload):
#     # Empaquetar el mensaje según tu formato
#     topic_b = topic.encode()
#     header = bytes([0x00, len(topic_b)]) + topic_b
#     frame = header + payload
#     outbox.push(frame)

#bus.subscribe("*", on_publish)

bus = MessageBus([outbox])

#############################################

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

#-----------------

WIDTH = 160
HEIGHT = 120
BUFSZ = WIDTH * HEIGHT *2  # 2*20800
SEND_INTERVAL = 1.0     # segundos entre envíos

# ---------- 1) GENERAR XCLK CON PWM PARA LA CÁMARA ----------
print("Configurando MCLK para OV7670 en GP22...")
pwm = PWM(Pin(mclk_pin_no))
pwm.freq(30_000_000)
pwm.duty_u16(32768)

# ---------- 2) INICIALIZAR I2C y OV7670 ----------
print("Inicializando I2C y OV7670...")
i2c = I2C(0, freq=400_000, scl=Pin(scl_pin_no), sda=Pin(sda_pin_no))
buf = bytearray(BUFSZ)

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
    #frame_buf = bytearray(width * height * 2)
    #gc.collect()
    def make_column_image():
        ov7670.capture(buf)
        return buf


except Exception as e:
    print(f"❌ Error al inicializar la cámara OV7670: {e}")
    #sys.exit(1)
    def make_column_image():
        global buf
        for x in range(WIDTH):
            v = int(x * 255 / (WIDTH - 1))
            for y in range(HEIGHT):
                buf[2*(y * WIDTH + x)] = buf[2*(y * WIDTH + x)+1] = v
        return buf




def thread_task():
    while True:
        bus.publish("camera/frame", make_column_image())
        time.sleep(SEND_INTERVAL)
        
        

_thread.start_new_thread(thread_task, ())

# CONFIG ------------------------------------------------
SSID = "PEREZ"
with open(".env") as file:
    PASSWORD = file.read()
HOST = "0.0.0.0"        # "" para escuchar en todas las interfaces
HTTP_PORT = 80
WS_PORT = 80     # usaremos el mismo socket HTTP y upgrade a /ws

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
    #print('payload',L)
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


import time

def log(msg, topic="debugPy/general"):
    t = time.localtime()
    formatted_time = "{:02}:{:02}:{:02}".format(t[3], t[4], t[5])
    line = "[{}] {}".format(formatted_time, msg).encode()
    bus.publish(topic, line)
    print('log', topic, len(line))

    

# Socket principal (sirve HTTP y puede hacer upgrade a WS en /ws)
print('socket',socket.getaddrinfo(HOST, HTTP_PORT))
addr = socket.getaddrinfo(HOST, HTTP_PORT)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
s.settimeout(None)
print("Servidor HTTP/WebSocket escuchando en", addr)
log('pru')
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
                    #log('envia')
                    while True:
#                         buf = make_column_image()  
#                         ws_send_binary(cl, buf)
#                         time.sleep(SEND_INTERVAL)
                        frame = outbox.pop()
                        #print('frame',frame)
                        if frame:
                            ws_send_binary(cl, frame)
                        else:
                            time.sleep(0.01)  # pausa pequeña para no saturar CPU

                except Exception as e:
                    print("Cliente WS desconectado o error:", e)
                finally:
                    cl.close()
            else:
                # Servir página HTML (GET /)
                
                
                heder="""
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Connection: close

"""
                with open("index_debug.html") as file:
                    html=file.read()
                cl.send((heder+html).encode())
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
    
    
