import ps3hid

from time import sleep

def ps3events(freq=1000, diag=False):
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
                for d in s.diff(sp):
                    yield d
            s = sp
            sleep(period)
    finally:
        ps3hid.close(h)
