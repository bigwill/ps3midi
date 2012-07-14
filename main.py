#!/usr/bin/env python

import ps3hid
import sys

from time import sleep

h = ps3hid.open()

diag = sys.argv[1] == '-d' if len(sys.argv) > 1 else False

try:
    s = None
    while True:
        sp = ps3hid.read(h)
        if not sp:
            continue
        if not s:
            s = sp
        if diag:
            sp.dump()
            print
        for d in s.diff(sp):
            print d
        s = sp
        sleep(.5)
except Exception, e:
    print 'Exception: %s' % repr(e)
finally:
    ps3hid.close(h)
