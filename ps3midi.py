#!/usr/bin/env python

import cProfile
import coremidi as cm
import midi as m
import sys

from collections import defaultdict
from itertools import izip
from ps3events import BUTTON_EVENT_NAMES, JOYSTICK_EVENT_NAMES, ps3events

# convert ps3 "analog" 0-255 to midi 0-127
def scale(v):
    return v/2

BUTTON_OFFSET = dict(izip(BUTTON_EVENT_NAMES.iterkeys(), (n for n in xrange(0, len(BUTTON_EVENT_NAMES)))))
ANALOG_CN = dict(izip(JOYSTICK_EVENT_NAMES.iterkeys(), (n for n in xrange(0, len(JOYSTICK_EVENT_NAMES)))))

def event_to_midi(e, base_note_num=24):
    ename = e[0]
    if ename in BUTTON_OFFSET:
        event_note = base_note_num + BUTTON_OFFSET[ename]
        (was_on, prev_pressure) = e[1]
        (is_on, cur_pressure) = e[2]

        if is_on and not was_on:
            return m.note_on(0, event_note, scale(cur_pressure))
        elif was_on and not is_on:
            return m.note_off(0, event_note, scale(prev_pressure))
        else:
            return m.note_aftertouch(0, event_note, scale(cur_pressure))
    elif ename in ANALOG_CN:
        (blank, ctrl_val) = e[2]
        return m.control_change(0, ANALOG_CN[ename], scale(ctrl_val))
    else:
        return None

def usage():
    print '%s [-p]' % sys.argv[0]
    print
    print "-p -- enables 'program mode', reducing analog sensitivity for easier MIDI mapping"
    print "-b -- specify mapping base note. Valid notes: C, C# .. B. Valid octaves: -1 .. 9"
    sys.exit(-1)

prof_mode = False # profiling
prog_mode = False
base_note = 'C1'
base_note_num = 24

# params handling
params = sys.argv[1:]
params.reverse()

while len(params) > 0:
    p = params.pop()
    if p == '-b':
        try:
            base_note = params.pop()
            base_note_num = m.midi_note_num(base_note)
        except:
            print "Invalid base note '%s'" % base_note
            print
            usage()
    elif p == '-p':
        prog_mode = True
    elif p == '-prof':
        prof_mode = True
    else:
        usage()
# end params handling

def main():
    print "PERF=%d PROG=%d PROFILE=%d BASE_NOTE=%s" % (not prog_mode, prog_mode, prof_mode, base_note)
    h = cm.open()

    for e in ps3events(prog_mode=prog_mode):
        me = event_to_midi(e, base_note_num=base_note_num)
        if me:
            cm.midi_send(h, [me])

if prof_mode:
    cProfile.run('main()')
else:
    main()
