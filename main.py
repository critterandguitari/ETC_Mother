import os
import pygame
import time
import etc_system
import imp
import socket
import traceback
import sys
import psutil
from pygame.locals import *
import osc
import sound
import filer
import osd
import liblo
print "starting..."

# create etc object
# this holds all the data (mode and preset names, knob values, midi input, sound input, current states, etc...)
# it gets passed to the modes which use the audio midi and knob values
# it gets operated on by the below modules (sound, OSC, file management, etc...)
etc = etc_system.System()

# just to make sure
etc.clear_flags()

# get our ip
etc.ip = socket.gethostbyname(socket.gethostname())

# setup osc
osc.init(etc)

# setup alsa sound
sound.init(etc)

# setup file manager
filer.init(etc)

# init pygame, this has to happen after sound is setup
# but before the graphics stuff below
pygame.init()
clocker = pygame.time.Clock() # for locking fps

# on screen display and other screen helpers
osd.init(etc)
osc.send("/led", 7) # set led to running

# init fb and main surfaces
print "opening frame buffer..."
hwscreen = pygame.display.set_mode(etc.RES,  pygame.FULLSCREEN | pygame.DOUBLEBUF, 32)
screen = pygame.Surface(hwscreen.get_size())
screen.fill((40,40,40)) 
hwscreen.blit(screen, (0,0))
pygame.display.flip()
hwscreen.blit(screen, (0,0))
pygame.display.flip()
time.sleep(2)

# load modes, post banner if none found
print "loading modes..."
if not (filer.load_modes()) :
    print "no modes found."
    osd.loading_banner(hwscreen, "No Modes found.  Insert USB drive with Modes folder and restart.")
    while True:
        # quit on esc
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
        time.sleep(1)

# run setup functions if modes have them
for i in range(0, len(etc.mode_names)-1) :
    try :
        etc.set_mode_by_index(i)
        mode = sys.modules[etc.mode]
        print etc.mode_root
        mode.setup(screen, etc)
        osd.loading_banner(hwscreen,"Loaded " + str(etc.mode) + ". Memory used: " + str(psutil.virtual_memory()[2]) )
    except AttributeError :
        print "no setup found"
        continue 

# load screen grabs
filer.load_grabs()

# used to measure fps
start = time.time()

# set initial mode
etc.set_mode_by_index(0)
mode = sys.modules[etc.mode]

time.sleep(1)

while 1:
    
    #check for OSC
    osc.recv()

    #send get midi and knobs for next time
    osc.send("/nf", 1) 

    # get knobs1-5
    etc.update_knobs()

    # quit on esc
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()

    # measure fps
    etc.frame_count += 1
    if ((etc.frame_count % 50) == 0):
        now = time.time()
        etc.fps = 1 / ((now - start) / 50)
        start = now

    # check for sound
    sound.recv()

    # set the mode on which to call drawi
# TODO if the module is no longer in sys (like got deleted and not reloaded, this will error,
# so use exception
    mode = sys.modules[etc.mode]

    if etc.clear_screen:
        screen.fill(etc.bg_color) 

    if etc.auto_clear :
        screen.fill(etc.bg_color) 

    etc.bg_color =  etc.color_picker_bg()
    
    # reload mode
    if etc.reload_mode :
        etc.error = ''
        # delete the old, and reload
        if etc.mode in sys.modules:  
            del(sys.modules[etc.mode]) 
        print "deleted module, reloading"
        try :
            mode = imp.load_source(etc.mode, etc.mode_root+'/main.py')
            print "reloaded"
            # then call setup
            try :
                mode.setup(screen, etc)
            except Exception, e:
                etc.error = traceback.format_exc()
                print "error with setup: " + etc.error
        except Exception, e:
            etc.error = traceback.format_exc()
            print "error reloading: " + etc.error
    
    # draw it
    try :
        mode.draw(screen, etc)
    except Exception, e:
        etc.error = traceback.format_exc()
 
    #save frame
    if etc.screengrab:
        filer.screengrab(screen)
  
    #draw the main screen, limit fps 30
    clocker.tick(30)
    hwscreen.blit(screen, (0,0))
    
    # osd
    if etc.osd :
        osd.render_overlay(hwscreen)

    pygame.display.flip()

    if etc.quit :
        sys.exit()
    
    # clear all the events
    etc.clear_flags()
    osc_msgs_recv = 0

time.sleep(1)

print "Quit"

