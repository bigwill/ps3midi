Intro
-----

Early cut of a project to generate MIDI messages from a PS3 controller. Currently only works on Mac OS X 10.7 (though could be easily adapted to other verisons).

Setup
-----

    $ make
    $ python ps3midi.py lightsaber -b A0

Watch the MIDI fly

Modules
-------

ps3hid.py - read PS3 controller device state
ps3events.py - get an event stream of controller state changes
midi.py - format MIDI messages

Acknowledgements
----------------

hid.c and hidapi.h were taken from Alan Ott's hidapi repo: http://github.com/signal11/hidapi . I will work to make this work repo relationship more sane way in the future