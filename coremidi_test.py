import coremidi
import midi

from time import sleep

h = coremidi.open()

def main():
    print "starting...."
    sleep(3)

    packets = [midi.note_on(0, 65, 120),
               midi.note_on(0, 68, 120),
               midi.note_on(0, 80, 120)]
    coremidi.midi_send(h, packets)
    print "note on..."

    sleep(.5)

    packets = [midi.note_aftertouch(0, 65, 60)]
    coremidi.midi_send(h, packets)
    print "note aftertouch 1..."

    sleep(.5)

    packets = [midi.note_aftertouch(0, 65, 30),
               midi.note_aftertouch(0, 68, 60)]
    coremidi.midi_send(h, packets)
    print "note aftertouch 2..."

    sleep(.5)

    packets = [midi.note_aftertouch(0, 65, 10),
               midi.note_aftertouch(0, 68, 30),
               midi.note_aftertouch(0, 80, 60)]
    coremidi.midi_send(h, packets)
    print "note aftertouch 3..."

    sleep(.5)

    packets = [midi.note_off(0, 65, 120),
               midi.note_off(0, 68, 120),
               midi.note_off(0, 80, 120)]
    coremidi.midi_send(h, packets)
    print "note off..."
    sleep(3)

main()
