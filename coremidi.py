from ctypes import *

cf = CDLL("/Developer/SDKs/MacOSX10.7.sdk/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")

cf.CFStringCreateWithCString.argtypes = [c_void_p, c_char_p, c_int]
cf.CFStringCreateWithCString.restype = c_void_p

cm = CDLL("/Developer/SDKs/MacOSX10.7.sdk/System/Library/Frameworks/CoreMIDI.framework/CoreMIDI")

class MIDIPacket(Structure):
    _fields_ = [("timestamp", c_ulonglong),
                ("length", c_ushort),
                ("data", c_ubyte*256),
                ]

def midi_list_size(n):
    class MIDIPacketList(Structure):
        _fields_ = [("num_packets", c_ulong),
                    ("packet", MIDIPacket*n),
                    ]
    return MIDIPacketList

cm.MIDIClientCreate.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
cm.MIDIClientCreate.restype = c_int

cm.MIDIOutputPortCreate.argtypes = [c_void_p, c_void_p, c_void_p]
cm.MIDIOutputPortCreate.restype = c_int

cm.MIDISourceCreate.argtypes = [c_void_p, c_void_p, c_void_p]
cm.MIDISourceCreate.restype = c_int

cm.MIDISend.argtypes = [c_void_p, c_void_p, c_void_p]
cm.MIDISend.restype = c_int

cm.MIDIPacketListInit.argtypes = [c_void_p]
cm.MIDIPacketListInit.restype = c_void_p

cm.MIDIPacketListAdd.argtypes = [c_void_p, c_uint, c_void_p, c_ulonglong, c_uint, c_void_p]
cm.MIDIPacketListAdd.restype = c_void_p


def _create_client(client_name):
    client_name_ref = cf.CFStringCreateWithCString(0, client_name, 0x0600)
    client_ref = c_void_p()
    r = cm.MIDIClientCreate(client_name_ref, 0, 0, byref(client_ref))
    if r != 0:
        assert False, 'Got result: %d' % r
    return client_ref

def _create_port(client_ref, port_name):
    port_name_ref = cf.CFStringCreateWithCString(0, port_name, 0x0600)
    port_ref = c_void_p()
    r = cm.MIDIOutputPortCreate(client_ref, port_name_ref, byref(port_ref))
    if r != 0:
        assert False, 'Got result: %d' % r
    return port_ref

def _create_source(client_ref, source_name):
    source_name_ref = cf.CFStringCreateWithCString(0, source_name, 0x0600)
    source_ref = c_void_p()
    r = cm.MIDISourceCreate(client_ref, source_name_ref, byref(source_ref))
    if r != 0:
        assert False, 'Got result: %d' % r
    return source_ref

def open():
    c = _create_client("ps3midi")
    p = _create_port(c, "ps3midi")
    s = _create_source(c, "ps3midi")
    return (p, s)

def midi_send((p, s), packets):
    plist = midi_list_size(len(packets))()
    ppacket_ref = cm.MIDIPacketListInit(byref(plist))
    lsize = 0
    for p in packets:
        print 'p'
        lp = len(p)
        ppacket_ref = cm.MIDIPacketListAdd(byref(plist), lsize, ppacket_ref, 0, lp, p)
        lsize += lp

    return plist
#    cm.MIDISend(p, s, byref(plist))
