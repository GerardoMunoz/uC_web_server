import digitalio
import busio
import board

from adafruit_ov7670 import (  # pylint: disable=unused-import
    OV7670,
    OV7670_SIZE_DIV16,
    OV7670_COLOR_YUV,OV7670_COLOR_RGB,
    OV7670_TEST_PATTERN_COLOR_BAR_FADE,
)

class OV7670_30x40_RGB565:
    def __init__(self,d0_d7pinslist,plk,xlk,sda,scl,hs,vs,ret,pwdn):
        cam_bus = busio.I2C(scl=scl, sda=sda)

        cam = OV7670(
            cam_bus,
            data_pins=d0_d7pinslist,
            clock=plk,
            vsync=vs,
            href=hs,
            mclk=xlk,
            shutdown=pwdn,
            reset=ret
        )
        cam.size = OV7670_SIZE_DIV16
        cam.colorspace = OV7670_COLOR_RGB
        cam.flip_y = False

        self.cam=cam
        #self.width = cam.width
        self.buf = bytearray(2 * cam.width * cam.height)

        
    def __call__(self):
        self.cam.capture(self.buf)
        return self.buf
        
        

