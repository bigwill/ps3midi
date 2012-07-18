import ps3hid

from ctypes import *
from ps3hid import BUTTONS, JOYSTICKS, TRIGGERS
from time import sleep


def ps3events(def_vel=120, diag=False, prog_mode=False):
    h = ps3hid.open()

    try:
        s = ps3hid.PS3State()
        cr = cast(byref(s), c_char_p)

        # init state
        while True:
            r = ps3hid.read(h, cr)
            if r:
                break

        sp = ps3hid.PS3State()
        crp = cast(byref(sp), c_char_p)

        while True:
            r = ps3hid.read(h, crp)
            if not r:
                continue
            if diag:
                sp.dump()
                print
            for d in s.diff(sp, def_vel=def_vel, min_v_delta=5 if prog_mode else 1):
                yield d
            (s, cr, sp, crp) = (sp, crp, s, cr)
    finally:
        ps3hid.close(h)
