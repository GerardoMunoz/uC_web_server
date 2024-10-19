from ov7670 import OV7670_30x40_RGB565 as CAM
import digitalio
import busio
import board

cam1=CAM(
    d0_d7pinslist=[
            board.GP0,
            board.GP1,
            board.GP2,
            board.GP3,
            board.GP4,
            board.GP5,
            board.GP6,
            board.GP7,
        ],
    plk=board.GP8,
    xlk=board.GP9,
    sda=board.GP20,
    scl=board.GP21,
    hs=board.GP12,
    vs=board.GP13,
    ret=board.GP14,
    pwdn=board.GP15
    )

def api( received):
    return cam1()




# def api( received):
#     # This function should interface with the OV7670 camera module and capture a 30x40 image.
#     # Replace this with actual implementation for your setup.
#     # Here we will use a dummy image with RGB565 data.
#     
#     width, height = 40, 30
#     image_data = bytearray(width * height * 2)  # RGB565 uses 2 bytes per pixel
# 
#     # Dummy image: all pixels set to green (0x07E0 in RGB565)
#     for i in range(0, len(image_data), 2):
#         image_data[i] = 0x07
#         image_data[i + 1] = 0xE0
# 
#     return image_data
# 
# 
# 
# 
# def api( received):    
#     # Example response for the /api request
#     response_data = '{"message": "Hello from Raspberry Pi Pico W!", "status": "success"}'
#     http_response = (
#         "HTTP/1.1 200 OK\r\n"
#         "Content-Type: application/json\r\n"
#         "Connection: close\r\n\r\n"
#         + response_data
#     )
#     return http_response
# 
# 
# 
# import re
# def api(client,request_str):
#     match = re.search(r'GET /api\?([^\s]+) HTTP', request_str)
#     if match:
#         query_string = match.group(1)
#         params = query_string.split('&')
#         json_data = {}
#         for param in params:
#             key, value = param.split('=')
#             json_data[key] = value
# 
#         print("Received JSON data:")
#         print(json.dumps(json_data))  # Pretty print the JSON data
# 
#     client.send("HTTP/1.1 200 OK\r\n")
#     client.send("Content-Type: text/plain\r\n")
#     client.send("Connection: close\r\n\r\n")
#     client.send(json.dumps({"status": "success", "received_data": json_data}).encode('utf-8'))
