#!/usr/bin/env python

import coremidi as cm
import midi as m

from itertools import izip
from ps3events import ps3events, BUTTON_EVENT_NAMES

# convert ps3 "analog" 0-255 to midi 0-127
def scale(v):
    return v/2

button_note = dict(izip(BUTTON_EVENT_NAMES.iterkeys(), (n for n in xrange(24, 24+len(BUTTON_EVENT_NAMES)))))
def event_to_midi(e):
    event_note = button_note.get(e[0], -1)
    if event_note == -1:
        print e
        return None
    (was_on, prev_pressure) = e[1]
    (is_on, cur_pressure) = e[2]
    if is_on and not was_on:
        return m.note_on(0, event_note, scale(cur_pressure))
    elif was_on and not is_on:
        return m.note_off(0, event_note, scale(prev_pressure))
    else:
        return m.note_aftertouch(0, event_note, scale(cur_pressure))

h = cm.open()

for e in ps3events():
    me = event_to_midi(e)
    if me:
        cm.midi_send(h, [me])
