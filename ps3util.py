#!/usr/bin/env python

from ps3events import ps3events
import sys

from time import sleep

diag = False
quiet = False # suppress (high volume) analog and accel. data, which is useful sometimes

for p in sys.argv[1:]:
    if p == '-d':
        diag = True
    elif p == '-q':
        quiet = True

freq = 2 if diag else 1000

for e in ps3events(freq=freq, diag=diag):
    fname = e[0]
    if quiet and (fname  == 'accelerator' or fname.find("analog") != -1):
        continue
    print e

