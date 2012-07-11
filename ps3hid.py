from ctypes import *

class PS3State(Structure):
    _fields_ = [("hid_channel", c_ubyte),
                ("unknown1", c_ubyte),
                ("button_states", c_ubyte*3),
                ("unknown2", c_ubyte),
                ("left_analog_horiz", c_ubyte),
                ("left_analog_vert", c_ubyte),
                ("right_analog_horiz", c_ubyte),
                ("right_analog_vert", c_ubyte),
                ("unknown_axes", c_ubyte*4),
                ("button_pressures", c_ubyte*12),
                ("unknown3", c_ubyte*3),
                ("status", c_ubyte),
                ("power_rating", c_ubyte),
                ("status2", c_ubyte),
                ("unknown4", c_ubyte*9),
                ("accelerator", c_ubyte*6),
                ("z_gyro", c_ubyte*2),
                ]
                 
ps3 = CDLL("libPS3hid.A.dylib")

ps3.ps3_open.restype = c_void_p

ps3.ps3_close.argtypes = [c_void_p]

ps3.ps3_read.argtypes = [c_void_p, c_char_p]
ps3.ps3_read.restype =  c_int

open = ps3.ps3_open
close = ps3.ps3_close

def read(h):
    s = PS3State()
    r = ps3.ps3_read(h, cast(byref(s), c_char_p))
    if r > 0:
        assert r == sizeof(PS3State), 'Received payload of unexpected size: %d' % r
        return s
    else:
        return None
