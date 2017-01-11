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
    midi_blob = args[0]
    #print "received message: " + str(args)
#    etc.update_knob(0, float(midi_blob[16]) / 127)
#    etc.update_knob(1, float(midi_blob[17]) / 127)
#    etc.update_knob(2, float(midi_blob[18]) / 127)
#    etc.update_knob(3, float(midi_blob[19]) / 127)
#    etc.update_knob(4, float(midi_blob[20]) / 127)
    etc.midi_clk = midi_blob[21] 
    etc.midi_pgm = midi_blob[22]
    
    # parse the notes outta the bit field
    for i in range(0, 16) :
        for j in range(0, 8) :
            if midi_blob[i] & (1<<j) :
                etc.notes[(i * 8) + j] = 1
            else :
                etc.notes[(i * 8) + j] = 0

def set_callback(path, args):
    global etc
    name = args[0]
    etc.set_mode_by_name(name)
    print "set patch to: " + str(etc.mode) + " with index " + str(etc.mode_index)
    
def reload_callback(path, args):
    global etc
    print "reloading: " + str(etc.mode)
    etc.reload_mode = True
    

def knobs_callback(path, args):
    global etc
    k1, k2, k3, k4, k5, k6 = args
    #print "received message: " + str(args)
    etc.update_knob(0, float(k4) / 1023)
    etc.update_knob(1, float(k1) / 1023)
    etc.update_knob(2, float(k2) / 1023)
    etc.update_knob(3, float(k5) / 1023)
    etc.update_knob(4, float(k3) / 1023)

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

    #print str(k) + " " + str(v)


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
    osc_server.add_method("/mblob", 'b', mblob_callback)
    osc_server.add_method("/reload", 'i', reload_callback)
  #  osc_server.add_method("/new", 's', reload_callback)
    osc_server.add_method("/set", 's', set_callback)
    osc_server.add_method(None, None, fallback)

def recv() :
    global osc_server
    while (osc_server.recv(1)):
        pass

def send(addr, args) :
    global osc_target
    liblo.send(osc_target, addr, args) 
