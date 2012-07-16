from ctypes import *
from itertools import izip

libc = CDLL("libSystem.dylib")

libc.memcmp.argtypes = [c_void_p, c_void_p, c_int]
libc.memcmp.restype = c_int

class PS3State(Structure):
    BUTTONS = ["left",
               "down",
               "right",
               "up",
               "start",
               "right_hat",
               "left_hat",
               "select",
               "square",
               "ex",
               "circle",
               "triange",
               "r1",
               "l1",
               "r2",
               "l2",
               "blank",
               "blank",
               "blank",
               "blank",
               "blank",
               "blank",
               "blank",
               "ps"
               ]

    _fields_ = [("hid_channel", c_ubyte),
                ("unknown1", c_ubyte),
                ("button_states", c_ubyte*3),
                ("unknown2", c_ubyte),
                ("left_analog_horiz", c_ubyte),
                ("left_analog_vert", c_ubyte),
                ("right_analog_horiz", c_ubyte),
                ("right_analog_vert", c_ubyte),
                ("unknown_axes", c_ubyte*4),
                ("up_pressure", c_ubyte),
                ("right_pressure", c_ubyte),
                ("down_pressure", c_ubyte),
                ("left_pressure", c_ubyte),
                ("l2_pressure", c_ubyte),
                ("r2_pressure", c_ubyte),
                ("l1_pressure", c_ubyte),
                ("r1_pressure", c_ubyte),
                ("triangle_pressure", c_ubyte),
                ("circle_pressure", c_ubyte),
                ("ex_pressure", c_ubyte),
                ("square_pressure", c_ubyte),
                ("unknown3", c_ubyte*3),
                ("status", c_ubyte),
                ("power_rating", c_ubyte),
                ("status2", c_ubyte),
                ("unknown4", c_ubyte*9),
                ("accelerator", c_ubyte*6),
                ("z_gyro", c_ubyte*2),
                ]

    def dump(self):
        for f in self._fields_:
            v = self.__getattribute__(f[0])
            if isinstance(v, int):
                d = '%02x' % v
            else: # byte array
                d = ''.join('%02x' % b for b in v)
            print '%18s = %24s' % (f[0], d)

    def _unpack_button_states(self, button_states):
        return [int(d) for d in ''.join([bin(256+byte)[3:] for byte in button_states])]

    def diff(self, other):
        for f in self._fields_:
            fname = f[0]
            v = self.__getattribute__(fname)
            vp = other.__getattribute__(fname)
            if isinstance(v, int):
                if v != vp:
                    yield (fname, v, vp)
            elif libc.memcmp(v, vp, sizeof(v)) != 0:
                if fname == "button_states":
                    bs = self._unpack_button_states(v)
                    bps = self._unpack_button_states(vp)
                    for (button, b, bp) in izip(self.BUTTONS, bs, bps):
                        if button == "blank":
                            continue
                        if b != bp:
                            yield (button, b, bp)
                else:
                    yield (fname, v, vp)

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
