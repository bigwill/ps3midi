#!/usr/bin/env python

import ps3hid
import sys

from time import sleep

h = ps3hid.open()

diag = sys.argv[1] == '-d' if len(sys.argv) > 1 else False

stime = .5 if diag else .0001

try:
    s = None
    while True:
        sp = ps3hid.read(h)
        if not sp:
            continue
        if diag:
            sp.dump()
            print
        else:
            if s:
                for d in s.diff(sp):
                    print d
        s = sp
        sleep(stime)
finally:
    ps3hid.close(h)
