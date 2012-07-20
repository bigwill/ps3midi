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
def scaleChar(v):
    assert 0 <= v <= 255, 'v (%d) out of expected range' % v
    r = v/2
    assert 0 <= r <= 127, 'result (%d) out of expected range' % r
    return r

# convert ps3 "analog" 0-65535 to midi 0-127
def scaleShort(v):
    assert 0 <= v <= 65535, 'v (%d) out of expected range' % v
    r = v/512
    assert 0 <= r <= 127, 'result (%d) out of expected range' % r
    return r

# convert 0-127 to 127-0
def invert(v):
    assert 0 <= v <= 127, 'v (%d) out of expected range' % v
    return 127-v

FILTER_C = 0.1
def lpf(a, ap):
    return ap * FILTER_C + a * (1-FILTER_C)

def build_mapper(note=BUTTONS + TRIGGERS, cc=JOYSTICKS, pitch=[], pitch_two_side=[]):
    NOTE_OFFSET = dict(izip(note, (n for n in xrange(0, len(note)))))
    ANALOG_CN = dict(izip(cc, (n for n in xrange(0, len(cc)))))

    assert (len(pitch) in [0, 2] or len(pitch_two_side) in [0, 2]) and len(pitch) != len(pitch_two_side), "only exactly two controls may be mapped to the pitch wheel"
    PITCH_WHEEL = OrderedDict(izip(pitch, [None, None]))
    PITCH_TWO_SIDE = OrderedDict(izip(pitch_two_side, [0, 0]))

    def event_to_midi(e, A, base_note_num=24):
        mes = []
        ename = e[0]

        # normalize and (maybe) filter parameters for output
        if ename.startswith('acc'):
            # update filter accelerometer state
            a = A[ename]
            ap = A[ename] = lpf(a, e[2][1])
            # modify event acc event with filtering & MIDI scale
            e = (e[0], (e[1][0], scaleShort(a)), (e[2][0], scaleShort(ap)))
        else:
            # normal event pressure/control value for MIDI scale
            e = (e[0], (e[1][0], scaleChar(e[1][1])), (e[2][0], scaleChar(e[2][1])))

        if ename in NOTE_OFFSET:
            event_note = base_note_num + NOTE_OFFSET[ename]
            (was_on, prev_pressure) = e[1]
            (is_on, cur_pressure) = e[2]

            if is_on and not was_on:
                mes.append(m.note_on(0, event_note, cur_pressure))
            elif was_on and not is_on:
                mes.append(m.note_off(0, event_note, prev_pressure))
            else:
                mes.append(m.note_aftertouch(0, event_note, cur_pressure))

        if ename in ANALOG_CN:
            (blank, ctrl_val) = e[2]
            mes.append(m.control_change(0, ANALOG_CN[ename], invert(ctrl_val)))

        if ename in PITCH_WHEEL:
            PITCH_WHEEL[ename] = e[2][1]
            [ph, pl] = PITCH_WHEEL.values()
            if ph and pl:
                mes.append(m.pitch_wheel(0, invert(ph) * 128 + invert(pl)))

        if ename in PITCH_TWO_SIDE:
            PITCH_TWO_SIDE[ename] = e[2][1]
            [pu, pd] = PITCH_TWO_SIDE.values()
            mes.append(m.pitch_wheel(0, int(8192 + 32.125 * (pu if pu >= pd else -pd))))

        return (mes, A)

    return event_to_midi

def usage():
    print 'Usage: %s mode [-p]' % sys.argv[0]
    print
    print "Valid modes:"
    for m in MODES:
        print '  %s' % m
    print
    print "-p       - enables 'program mode', reducing analog sensitivity for easier MIDI mapping"
    print "-b       - specify mapping base note. Valid notes: C, C# .. B. Valid octaves: -1 .. 9"
    print "-ps3spy  - Spy mode for PS3 event stream"
    print "-midispy - Spy mode for MIDI event stream"
    print "-prof    - analyze performance"
    sys.exit(-1)

prof_mode = False # profiling
prog_mode = False
base_note = 'C1'
base_note_num = 24
ps3spy = False

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
    elif p == '-ps3spy':
        ps3spy = True
    elif p == '-midispy':
        m.SPY = True
    else:
        print "Unknown parameters '%s'" % p
        print
        usage()
# end params handling

def main():
    print "PERF=%d PROG=%d PROFILE=%d BASE_NOTE=%s" % (not prog_mode, prog_mode, prof_mode, base_note)
    h = cm.open()
    A = {"accX" : 32768,
         "accY" : 32768,
         "accZ" : 32768}

    for e in ps3events(prog_mode=prog_mode):
        if ps3spy:
            print e
        (mes, A) = event_to_midi(e, A, base_note_num=base_note_num)
        if mes:
            cm.midi_send(h, mes)

if prof_mode:
    cProfile.run('main()')
else:
    main()
