from ctypes import *
from itertools import izip

libc = CDLL("libSystem.dylib")

libc.memcmp.argtypes = [c_void_p, c_void_p, c_int]
libc.memcmp.restype = c_int

class PS3State(Structure):
    BUTTON_STATE_BITS = ["left",
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
                         "triangle",
                         "r1",
                         "l1",
                         "r2",
                         "l2",
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         "ps"
                         ]

    BUTTONS = [x for x in BUTTON_STATE_BITS if x]

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

    def _unpacked_button_states(self):
        button_states = self.__getattribute__("button_states")
        return [int(d) for d in ''.join([bin(256+byte)[3:] for byte in button_states])]

    def _button_pressure(self, button, def_vel):
        fname = '%s_pressure' % button
        try:
            return self.__getattribute__(fname)
        except:
            return def_vel

    def diff(self, other, def_vel=120, min_v_delta=1):
        for f in self._fields_:
            fname = f[0]
            # buttons and related pressures special based below
            if fname == "button_states" or fname.endswith('pressure'):
                continue

            v = self.__getattribute__(fname)
            vp = other.__getattribute__(fname)
            if isinstance(v, int): # 0-255 parameters (e.g., one analog stick axis)
                if abs(v - vp) >= min_v_delta:
                    yield (fname, (0, v), (0, vp))
            else:
            # just ignore non-int values for now (just accelerator data at the moment)
                continue
#            elif libc.memcmp(v, vp, sizeof(v)) != 0:
#                yield (fname, (0, v), (0, vp))

        # unpack button bits and related pressures
        bs = self._unpacked_button_states()
        bps = other._unpacked_button_states()
        for (button, b, bp) in izip(self.BUTTON_STATE_BITS, bs, bps):
            if not button:
                continue
            p = self._button_pressure(button, def_vel)
            pp = other._button_pressure(button, def_vel)
            if b != bp or p != pp:
                yield (button, (b, p), (bp, pp))

hid = CDLL("libHid.A.dylib")

hid.hid_open.restype = c_void_p

hid.hid_close.argtypes = [c_void_p]

hid.hid_read.argtypes = [c_void_p, c_void_p, c_int]
hid.hid_read.restype = c_int

def open():
    return hid.hid_open(0x54c, 0x0268, 0);

def close(h):
    hid.hid_close(h)

req_state_buf = create_string_buffer('\x01\x81', 17)
REQ_STATE_BUF_SIZE = sizeof(req_state_buf)
PS3_STATE_SIZE = sizeof(PS3State)

def read(h):
    s = PS3State()
    r = hid.hid_read(h, cast(byref(s), c_char_p), PS3_STATE_SIZE)
    if r > 0:
        assert r == PS3_STATE_SIZE, 'Received payload of unexpected size: %d' % r
        return s
    else:
        return None
