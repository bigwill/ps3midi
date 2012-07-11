import struct

TYPES = (128, 144, 160, 176)
def assert_valid_type(type):
    if type in TYPES:
        return
    assert False, 'type %d not in expected set: %s' % (type, TYPES)

def assert_range(v, l, h):
    if l <= v <= h:
        return
    assert False, 'value %d not in %d to %d' % (v, l, h)

def kv_base(type, chan, k, v):
    assert_valid_type(type)
    assert_range(chan, 0, 15)
    assert_range(k, 0, 127)
    assert_range(v, 0, 127)
    return struct.pack('BBB', type + chan, k, v)

def note_off(chan, note, vel):
    return kv_base(128, chan, note, vel)

def note_on(chan, note, vel):
    return kv_base(144, chan, note, vel)

def key_aftertouch(chan, note, pressure):
    return kv_base(160, chan, note, pressure)

def control_change(chan, note, val):
    return kv_base(176, chan, note, val)

def prog_change(chan, prog):
    assert_range(chan, 0, 127)
    assert_range(prog, 0, 127)
    return struct.pack('BB', 192 + chan, prog)

def chan_aftertouch(chan, pressure):
    assert_range(chan, 0, 127)
    assert_range(pressure, 0, 127)
    return struct.pack('BB', 208 + chan, pressure)

def pitch_wheel(chan, pitch):
    assert_range(chan, 0, 127)
    assert_range(pitch, 0, 16383) # 14 bit value
    ph = pitch / 128 # top 7 bits
    pl = pitch % 128 # bottom 7 bits
    return struct.pack('BBB', 224 + chan, ph, pl)

