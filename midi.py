import struct

TYPES = (128, 144, 160, 176)
def _assert_valid_type(type):
    if type in TYPES:
        return
    assert False, 'type %d not in expected set: %s' % (type, TYPES)

def _assert_range(v, l, h):
    if l <= v <= h:
        return
    assert False, 'value %d not in %d to %d' % (v, l, h)

def _kv_base(type, chan, k, v):
    _assert_valid_type(type)
    _assert_range(chan, 0, 15)
    _assert_range(k, 0, 127)
    _assert_range(v, 0, 127)
    return struct.pack('BBB', type + chan, k, v)

# MIDI message formatters
def note_off(chan, note, vel):
    return _kv_base(128, chan, note, vel)

def note_on(chan, note, vel):
    return _kv_base(144, chan, note, vel)

def note_aftertouch(chan, note, pressure):
    return _kv_base(160, chan, note, pressure)

def control_change(chan, ctlr, val):
    return _kv_base(176, chan, ctlr, val)

def prog_change(chan, prog):
    _assert_range(chan, 0, 127)
    _assert_range(prog, 0, 127)
    return struct.pack('BB', 192 + chan, prog)

def chan_aftertouch(chan, pressure):
    _assert_range(chan, 0, 127)
    _assert_range(pressure, 0, 127)
    return struct.pack('BB', 208 + chan, pressure)

def pitch_wheel(chan, pitch):
    _assert_range(chan, 0, 127)
    _assert_range(pitch, 0, 16383) # 14 bit value
    ph = pitch / 128 # top 7 bits
    pl = pitch % 128 # bottom 7 bits
    return struct.pack('BBB', 224 + chan, ph, pl)

# Other helpful functions

# This might make more sense if you look at:
# http://midikits.net23.net/midi_analyser/midi_note_numbers_for_octaves.htm
_OCTAVE_MAP = { 'C'  : 0,
                'C#' : 1,
                'D'  : 2,
                'D#' : 3,
                'E'  : 4,
                'F'  : 5,
                'F#' : 6,
                'G'  : 7,
                'G#' : 8,
                'A'  : 9,
                'A#' : 10,
                'B'  : 11,
                }
def midi_note_num(note):
    note = note.upper()
    if note.find('#') != -1:
        norm_note = note[:2]
        octave = int(note[2:])
    else:
        norm_note = note[:1]
        octave = int(note[1:])

    assert norm_note in _OCTAVE_MAP, "'%s' is not a valid note" % norm_note
    _assert_range(octave, -1, 9)
    n = 12 + 12 * octave + _OCTAVE_MAP[norm_note]
    _assert_range(n, 0, 127) # safety sake
    return n
