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

