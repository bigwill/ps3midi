#!/usr/bin/env python

import cProfile
import coremidi as cm
import midi as m
import sys

from config import MODES
from collections import OrderedDict
from itertools import izip
from ps3events import BUTTONS, TRIGGERS, JOYSTICKS, ps3events

# convert ps3 "analog" 0-255 to midi 0-127
def scale(v):
    assert 0 <= v <= 255, 'v out of expected range'
    return v/2

# convert 0-127 to 127-0
def invert(v):
    assert 0 <= v <= 127, 'v out of expected range'
    return 127-v

def build_mapper(note=BUTTONS + TRIGGERS, cc=JOYSTICKS, pitch=[], pitch_two_side=[]):
    NOTE_OFFSET = dict(izip(note, (n for n in xrange(0, len(note)))))
    ANALOG_CN = dict(izip(cc, (n for n in xrange(0, len(cc)))))

    assert (len(pitch) in [0, 2] or len(pitch_two_side) in [0, 2]) and len(pitch) != len(pitch_two_side), "only exactly two controls may be mapped to the pitch wheel"
    PITCH_WHEEL = OrderedDict(izip(pitch, [None, None]))
    PITCH_TWO_SIDE = OrderedDict(izip(pitch_two_side, [0, 0]))

    def event_to_midi(e, base_note_num=24):
        mes = []
        ename = e[0]
        if ename in NOTE_OFFSET:
            event_note = base_note_num + NOTE_OFFSET[ename]
            (was_on, prev_pressure) = e[1]
            (is_on, cur_pressure) = e[2]

            if is_on and not was_on:
                mes.append(m.note_on(0, event_note, scale(cur_pressure)))
            elif was_on and not is_on:
                mes.append(m.note_off(0, event_note, scale(prev_pressure)))
            else:
                mes.append(m.note_aftertouch(0, event_note, scale(cur_pressure)))

        if ename in ANALOG_CN:
            (blank, ctrl_val) = e[2]
            mes.append(m.control_change(0, ANALOG_CN[ename], invert(scale(ctrl_val))))

        if ename in PITCH_WHEEL:
            PITCH_WHEEL[ename] = e[2][1]
            [ph, pl] = PITCH_WHEEL.values()
            if ph and pl:
                mes.append(m.pitch_wheel(0, invert(scale(ph)) * 128 + invert(scale(pl))))

        if ename in PITCH_TWO_SIDE:
            PITCH_TWO_SIDE[ename] = e[2][1]
            [pu, pd] = PITCH_TWO_SIDE.values()
            mes.append(m.pitch_wheel(0, int(8192 + 32.125 * (pu if pu >= pd else -pd))))

        return mes

    return event_to_midi

def usage():
    print 'Usage: %s mode [-p]' % sys.argv[0]
    print
    print "Valid modes:"
    for m in MODES:
        print '  %s' % m
    print
    print "-p -- enables 'program mode', reducing analog sensitivity for easier MIDI mapping"
    print "-b -- specify mapping base note. Valid notes: C, C# .. B. Valid octaves: -1 .. 9"
    print "-s -- Spy mode. Watch the ps3events stream"
    print "-prof -- analyze performance"
    sys.exit(-1)

prof_mode = False # profiling
prog_mode = False
base_note = 'C1'
base_note_num = 24
spy = False

# params handling
mode = sys.argv[1]
if mode in MODES:
    event_to_midi = build_mapper(**MODES[mode])
else:
    print "Invalid mode '%s'" % mode
    print
    usage()

params = sys.argv[2:]
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
    elif p == '-s':
        spy = True
    else:
        print "Unknown parameters '%s'" % p
        print
        usage()
# end params handling

def main():
    print "PERF=%d PROG=%d PROFILE=%d BASE_NOTE=%s" % (not prog_mode, prog_mode, prof_mode, base_note)
    h = cm.open()

    for e in ps3events(prog_mode=prog_mode):
        if spy:
            print e
        mes = event_to_midi(e, base_note_num=base_note_num)
        if mes:
            cm.midi_send(h, mes)

if prof_mode:
    cProfile.run('main()')
else:
    main()
