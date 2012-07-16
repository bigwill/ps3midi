#!/usr/bin/env python

import ps3hid
import sys

from time import sleep

h = ps3hid.open()

diag = False
quiet = False # suppress (high volume) analog and accel. data, which is useful sometimes

for p in sys.argv[1:]:
    if p == '-d':
        diag = True
    elif p == '-q':
        quiet = True

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
                    fname = d[0]
                    if quiet and (fname  == 'accelerator' or fname.find("analog") != -1):
                        continue
                    print d
        s = sp
        sleep(stime)
finally:
    ps3hid.close(h)
