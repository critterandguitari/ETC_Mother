import sys
import liblo

etc = None 
osc_server = None
osc_target = None

# OSC callbacks
def fallback(path, args):
    pass


def mblob_callback(path, args):
    global etc
    #print "received message: " + str(args)
    etc.update_knob(0, float(args[0][0]) / 127)
    etc.update_knob(1, float(args[0][1]) / 127)
    etc.update_knob(2, float(args[0][2]) / 127)
    etc.update_knob(3, float(args[0][3]) / 127)
    etc.update_knob(4, float(args[0][4]) / 127)

def knobs_callback(path, args):
    global etc
    k1, k2, k3, k4, k5, k6 = args
    print "received message: " + str(args)
#    etc.update_knob(0, float(k4) / 1023)
#    etc.update_knob(1, float(k1) / 1023)
#    etc.update_knob(2, float(k2) / 1023)
#    etc.update_knob(3, float(k5) / 1023)
#    etc.update_knob(4, float(k3) / 1023)

def keys_callback(path, args) :
    global etc
    k, v = args
    if (k == 2 and v > 0) : etc.next_mode()
    if (k == 1 and v > 0) : etc.prev_mode()
    if (k == 9 and v > 0) : etc.trig = True
    if (k == 7 and v > 0) : etc.screengrab = True
    if (k == 4 and v > 0) : etc.prev_preset()
    if (k == 6 and v > 0) : etc.save_preset()
    if (k == 5 and v > 0) : etc.next_preset()
    if (k == 3 and v > 0) : 
        if (etc.osd) : etc.osd = False
        else : etc.osd = True
    if (k == 8 and v > 0) : 
        if (etc.auto_clear) : etc.auto_clear = False
        else : etc.auto_clear = True

    print str(k) + " " + str(v)

def midi_note_on_callback(path, args):
    global etc
    c, n, v = args
    etc.note_on = True
    etc.note_num = n
    etc.note_velocity = v

def midi_cc_callback(path, args):
    global etc
    c, n, v = args

    if n == 21 :
        etc.knob1 = float(v) / 127
    if n == 22 :
        etc.knob2 = float(v) / 127
    if n == 23 :
        etc.knob3 = float(v) / 127
    if n == 24 :
        etc.knob4 = float(v) / 127
    if n == 25 :
        etc.knob5 = float(v) / 127

def init (etc_object) :
   
    global osc_server, osc_target, etc

    etc = etc_object
    
# OSC init server and client
    try:
        osc_target = liblo.Address(4001)
    except liblo.AddressError as err:
        print(err)
        sys.exit()

    try:
        osc_server = liblo.Server(4000)
    except liblo.ServerError, err:
        print str(err)
        sys.exit()

    osc_server.add_method("/knobs", 'iiiiii', knobs_callback)
    osc_server.add_method("/key", 'ii', keys_callback)
    osc_server.add_method("/mnon", 'iii', midi_note_on_callback)
    osc_server.add_method("/mcc", 'iii', midi_cc_callback)
    osc_server.add_method("/setPatch", 's', midi_cc_callback)
    osc_server.add_method("/mblob", 'b', mblob_callback)
    osc_server.add_method(None, None, fallback)

def recv() :
    global osc_server
    while (osc_server.recv(1)):
        pass
    #osc_server.recv(0)

def send(addr, args) :
    global osc_target
    liblo.send(osc_target, addr, args) 
