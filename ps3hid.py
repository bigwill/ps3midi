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
                 
hid = CDLL("libHid.A.dylib")

hid.hid_open.restype = c_void_p

hid.hid_close.argtypes = [c_void_p]

hid.hid_read.argtypes = [c_void_p, c_void_p, c_int]
hid.hid_read.restype = c_int

hid.hid_write.argtypes = [c_void_p, c_void_p, c_int]
hid.hid_write.restype = c_int

def open():
    return hid.hid_open(0x54c, 0x0268, 0);

def close(h):
    hid.hid_close(h)

req_state_buf = create_string_buffer('\x01\x81', 17)
def read(h):
    r = hid.hid_write(h, req_state_buf, sizeof(req_state_buf))
    if r < 0:
        return None

    s = PS3State()
    r = hid.hid_read(h, cast(byref(s), c_char_p), sizeof(PS3State))
    if r > 0:
        assert r == sizeof(PS3State), 'Received payload of unexpected size: %d' % r
        return s
    else:
        return None