import os
import pygame
import time
import random
import glob
import mvp_system
import imp
import socket
import traceback
import sys
import liblo
from pygame.locals import *
import alsaaudio, audioop
 
#create mvp object
mvp = mvp_system.System()
mvp.clear_flags()

# OSC init
try:
    osc_server = liblo.Server(4000)
except liblo.ServerError, err:
    print str(err)
    sys.exit()

osc_msgs_recv = 0

def fallback(path, args):
    global osc_msgs_recv
    osc_msgs_recv += 1

def knobs_callback(path, args):
    global osc_msgs_recv
    osc_msgs_recv += 1
    global mvp
    k1, k2, k3, k4, k5, k6 = args
    #mvp.knob1l = float(k4) / 1023
    #mvp.knob2l = float(k1) / 1023
    #mvp.knob3l = float(k2) / 1023
    #mvp.knob4l = float(k5) / 1023
    #mvp.knob5l = float(k3) / 1023

def keys_callback(path, args) :
    global osc_msgs_recv
    osc_msgs_recv += 1
    global mvp
    k, v = args
    if (k == 2 and v > 0) : mvp.next_patch = True
    if (k == 1 and v > 0) : mvp.prev_patch = True
    if (k == 9 and v > 0) : mvp.clear_screen = True
    if (k == 7 and v > 0) : mvp.screengrab = True
    if (k == 4 and v > 0) : mvp.prev_preset()
    if (k == 6 and v > 0) : mvp.save_preset()
    if (k == 5 and v > 0) : mvp.next_preset()
    if (k == 3 and v > 0) : 
        if (mvp.osd) : mvp.osd = False
        else : mvp.osd = True
    if (k == 8 and v > 0) : 
        if (mvp.auto_clear) : mvp.auto_clear = False
        else : mvp.auto_clear = True

    print str(k) + " " + str(v)

def midi_note_on_callback(path, args):
    global osc_msgs_recv
    osc_msgs_recv += 1
    global mvp
    c, n, v = args
    mvp.note_on = True
    mvp.note_num = n
    mvp.note_velocity = v
    #print n

def midi_cc_callback(path, args):
    global osc_msgs_recv
    osc_msgs_recv += 1
    global mvp
    c, n, v = args

    if n == 21 :
        mvp.knob1l = float(v) / 127
    if n == 22 :
        mvp.knob2l = float(v) / 127
    if n == 23 :
        mvp.knob3l = float(v) / 127
    if n == 24 :
        mvp.knob4l = float(v) / 127
    if n == 25 :
        mvp.knob5l = float(v) / 127
#    print args


osc_server.add_method("/knobs", 'iiiiii', knobs_callback)
osc_server.add_method("/key", 'ii', keys_callback)
osc_server.add_method("/mnon", 'iii', midi_note_on_callback)
osc_server.add_method("/mcc", 'iii', midi_cc_callback)
osc_server.add_method(None, None, fallback)

last_time = time.time()
this_time = 0

while 1:
    
    #check for OSC
    while (osc_server.recv(1)):
        pass
    #osc_server.recv(0)

    # osd
    this_time = time.time()
    elapsed_time = this_time - last_time
    last_time = this_time
    osc_msgs_per_sec = osc_msgs_recv / elapsed_time
    txt = str('osc: ' + str(osc_msgs_recv) + ', osc / sec: ' + str(osc_msgs_per_sec)  )
    print txt

    if mvp.quit :
        sys.exit()
    
    # clear all the events
    mvp.clear_flags()
    osc_msgs_recv = 0

    time.sleep(1)


print "Quit"
