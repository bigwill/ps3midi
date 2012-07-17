#!/usr/bin/env python

import coremidi as cm
import midi as m
import sys

from collections import defaultdict
from itertools import izip
from ps3events import BUTTON_EVENT_NAMES, JOYSTICK_EVENT_NAMES, ps3events

# convert ps3 "analog" 0-255 to midi 0-127
def scale(v):
    return v/2

button_note = dict(izip(BUTTON_EVENT_NAMES.iterkeys(), (n for n in xrange(24, 24+len(BUTTON_EVENT_NAMES)))))
analog_cn = dict(izip(JOYSTICK_EVENT_NAMES.iterkeys(), (n for n in xrange(0, len(JOYSTICK_EVENT_NAMES)))))

def event_to_midi(e):
    event_note = button_note.get(e[0], -1)
    cn = analog_cn.get(e[0], -1)
    (was_on, prev_pressure) = e[1]
    (is_on, cur_pressure) = e[2]

    if event_note >= 0:
        if is_on and not was_on:
            return m.note_on(0, event_note, scale(cur_pressure))
        elif was_on and not is_on:
            return m.note_off(0, event_note, scale(prev_pressure))
        else:
            return m.note_aftertouch(0, event_note, scale(cur_pressure))
    elif cn >= 0:
        return m.control_change(0, cn, scale(cur_pressure))

def usage():
    print '%s [-p]' % sys.argv[0]
    print
    print "-p -- enables 'program mode', reducing analog sensitivity for easier MIDI mapping"
    sys.exit(-1)

prog_mode = False
for p in sys.argv[1:]:
    if p == '-p':
        prog_mode = True
    else:
        usage()

if prog_mode:
    print "Program mode..."
else:
    print "Performance mode..."

h = cm.open()

for e in ps3events(prog_mode=prog_mode):
    me = event_to_midi(e)
    if me:
        cm.midi_send(h, [me])
