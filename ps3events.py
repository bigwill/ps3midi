import ps3hid

from collections import OrderedDict
from time import sleep

BUTTON_EVENT_NAMES = OrderedDict([(b,True) for b in ps3hid.PS3State.BUTTONS if b])
JOYSTICK_EVENT_NAMES = OrderedDict([(f[0],True) for f in ps3hid.PS3State._fields_ if (f[0].find('analog') != -1)])

def ps3events(freq=1000, diag=False, prog_mode=False):
    h = ps3hid.open()
    period = float(1) / freq

    try:
        s = None
        while True:
            sp = ps3hid.read(h)
            if not sp:
                continue
            if diag:
                sp.dump()
                print
            if s:
                for d in s.diff(sp, min_v_delta=5 if prog_mode else 1):
                    yield d
            s = sp
            sleep(period)
    finally:
        ps3hid.close(h)
