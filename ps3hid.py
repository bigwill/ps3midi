from ctypes import *
from itertools import izip

libc = CDLL("libSystem.dylib")

libc.memcmp.argtypes = [c_void_p, c_void_p, c_int]
libc.memcmp.restype = c_int

class PS3State(Structure):
    CONTROL_STATE_FLAGS = ["left",
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

    TRIGGERS = ["l1", "r1", "l2", "r2"]
    BUTTONS = [x for x in CONTROL_STATE_FLAGS if x and x not in TRIGGERS]

    _fields_ = [("hid_channel", c_ubyte),
                ("unknown1", c_ubyte),
                ("control_states", c_ubyte*3),
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

    def _unpacked_control_states(self):
        control_states = self.__getattribute__("control_states")
        return [int(d) for d in ''.join([bin(256+byte)[3:] for byte in control_states])]

    def _control_pressure(self, control, def_vel):
        fname = '%s_pressure' % control
        try:
            return self.__getattribute__(fname)
        except:
            return def_vel

    def diff(self, other, def_vel=120, min_v_delta=1):
        for f in self._fields_:
            fname = f[0]
            # controls and related pressures special based below
            if fname == "control_states" or fname.endswith('pressure'):
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

        # unpack control bits and related pressures
        cs = self._unpacked_control_states()
        cps = other._unpacked_control_states()
        for (control, c, cp) in izip(self.CONTROL_STATE_FLAGS, cs, cps):
            if not control:
                continue
            p = self._control_pressure(control, def_vel)
            pp = other._control_pressure(control, def_vel)
            if c != cp or p != pp:
                yield (control, (c, p), (cp, pp))

hid = CDLL("libHid.A.dylib")

hid.hid_open.restype = c_void_p

hid.hid_close.argtypes = [c_void_p]

hid.hid_read.argtypes = [c_void_p, c_void_p, c_int]
hid.hid_read.restype = c_int

hid.hid_set_nonblocking.argtypes = [c_void_p, c_int]
hid.hid_set_nonblocking.restype = c_int

def open():
    h = hid.hid_open(0x54c, 0x0268, 0)
    hid.hid_set_nonblocking(h, 1)
    return h

def close(h):
    hid.hid_close(h)

PS3_STATE_SIZE = sizeof(PS3State)
def read(h, buf_ref):
    r = hid.hid_read(h, buf_ref, PS3_STATE_SIZE)
    if r > 0:
        assert r == PS3_STATE_SIZE, 'Received payload of unexpected size: %d' % r
        return buf_ref
    else:
        return None
