#https://github.com/pi3g/pico-w/tree/main/MicroPython/I%20Pico%20W%20LED%20web%20server
#https://youtu.be/Or-UVgiMQsU

import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
import socket


response="""

<!DOCTYPE html>
<html>
  <head>
    <title>three.js glb example</title>
    <meta charset="utf-8">
    <style>
      * {
        margin:0;
        padding:0
      }

      body {
        overflow:hidden;
      }
    </style>
  </head>
  <body>
        <h1>ARM</h1>
        <p>Control the onboard LED</p>
        <a href=\"?led=on\"><button>ON</button></a>&nbsp;
        <a href=\"?led=off\"><button>OFF</button></a>
        <a href=\"?led=quit\"><button>QUIT</button></a>
    <script type="module">
    import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.118/build/three.module.js';
    //import {FBXLoader} from 'https://cdn.jsdelivr.net/npm/three@0.118.1/examples/jsm/loaders/FBXLoader.js';
    import {GLTFLoader} from 'https://cdn.jsdelivr.net/npm/three@0.118.1/examples/jsm/loaders/GLTFLoader.js';

      var world, mass, body, shape, timeStep=1/60,
         camera, scene, renderer, geometry, material, 
         mesh,shoulder,loader,children,obj_by_name;

		initThree();
		const manager = new THREE.LoadingManager(onLoad);
      
		loader = new GLTFLoader( manager );
		loader.load( 'https://gerardomunoz.github.io/uC_web_server/RPiPicoMicroPython/threejs_glb/shoulder_blue.glb', function ( gltf ) {
			console.log("gltf")
			console.log(gltf.scene.children)
			children=[...gltf.scene.children]
			scene.add( gltf.scene );
		} );

       function onLoad(){
		  let child;
		  obj_by_name={};
		  console.log(children);
		  while (children.length != 0){
			  child=children.shift()
			  console.log(child["name"])
			  children.push(...child.children)
			  console.log(child.children)
			  obj_by_name[child["name"]]=child
		  }
		  console.log("obj_by_name",obj_by_name)
		  shoulder=obj_by_name["shoulder"]
		console.log('shoulder',shoulder)
		animate();
	  }


 
      function initThree() {

          scene = new THREE.Scene();

          camera = new THREE.PerspectiveCamera( 75, window.innerWidth*2 / window.innerHeight, 1, 100 );
          camera.position.set(4,5,6);
 //         camera.position.y = -5;
          camera.lookAt(0,0,0)
          scene.add( camera );
          renderer = new THREE.WebGLRenderer();
          renderer.setSize( window.innerWidth, window.innerHeight/2 );

          document.body.appendChild( renderer.domElement );

      }

      function animate() {

          requestAnimationFrame( animate );
          shoulder.rotation.x += 0.01;
		  //shoulder.rotation.y += 0.01;
          renderer.render( scene, camera );

      }

    </script>
  </body>
</html>


"""






# Set country to avoid possible errors
#rp2.country('DE')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

# Load login data from different file for safety reasons
wlan.connect('Ejemplo', '12345678')

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    
# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed ',wlan_status)
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    

# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(addr)

s.listen(1)

print('Listening on', addr)
led = machine.Pin('LED', machine.Pin.OUT)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        r = cl.recv(1024)
        # print(r)
        
        r = str(r)
        led_on = r.find('?led=on')
        led_off = r.find('?led=off')
        led_quit = r.find('?led=quit')
        print('led_on = ', led_on)
        print('led_off = ', led_off)
        print('led_quit = ', led_quit)
        if led_on > -1:
            print('LED ON')
            led.value(1)
            
        if led_off > -1:
            print('LED OFF')
            led.value(0)

        if led_quit > -1:
            print('QUIT')
            cl.close()
            #print('Connection closed')
            s.close()
            wlan.active(False)
            wlan.disconnect()
            print('Bye')
            break
            
        cl.send("HTTP/1.1 200 OK\r\n")
        cl.send("Content-Type: text/html\r\n")
        cl.send("Connection: close\r\n\r\n")
        chunk_size=1000
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            cl.send(chunk)
            time.sleep_ms(100)
        cl.close()

    except OSError as e:
        cl.close()
        print('Connection closed')

# Make GET request
#request = requests.get('http://www.google.com')
#print(request.content)
#request.close()