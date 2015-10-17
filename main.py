import os
import pygame
import time
import glob
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

# create etc object
# this holds all the data (mode and preset names, knob values, midi input, sound input, current states, etc...)
# it gets passed to the modes which use the midi and knob values
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

# init pygame
pygame.init()

# OSD stuff
font = pygame.font.SysFont(None, 32)
notemsg = font.render('...', True, etc.WHITE, etc.OSDBG)

# init fb and main surfaces
print "opening frame buffer"
hwscreen = pygame.display.set_mode(etc.RES,  pygame.FULLSCREEN | pygame.DOUBLEBUF, 32  )
screen = pygame.Surface(hwscreen.get_size())
screen.fill((40,40,40)) 
hwscreen.blit(screen, (0,0))
pygame.display.flip()
hwscreen.blit(screen, (0,0))
pygame.display.flip()
#liblo.send(osc_target, "/led", 7) # running
osc.send("/led", 5)
time.sleep(3)

# loading banner helper
def loading_banner(stuff) :
    global hwscreen
    screen.fill((40,40,40)) 
    font = pygame.font.SysFont(None, 40)
    text = font.render(stuff, True, etc.WHITE, (40,40,40))
    text_rect = text.get_rect()
    text_rect.x = 20
    text_rect.y = 20
    hwscreen.blit(text, text_rect)
    pygame.display.flip()

# load modes,  check if modes are found
print "loading modes..."
got_a_mode = False
mode_folders = filer.get_immediate_subdirectories(etc.MODES_PATH)

for mode_folder in mode_folders :
    mode_name = str(mode_folder)
    mode_path = etc.MODES_PATH+mode_name+'/main.py'
    print mode_path
    try :
        imp.load_source(mode_name, mode_path)
        got_a_mode = True
        etc.mode_names.append(mode_name)
    except Exception, e:
        print traceback.format_exc()

if not(got_a_mode) :
    print "no modes found."
    loading_banner("No Modes found.  Insert USB drive with Modes folder and restart.")
    while True:
        # quit on esc
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
        time.sleep(1)

# set initial mode
etc.cur_mode_index = 0
etc.mode = etc.mode_names[etc.cur_mode_index]
mode = sys.modules[etc.mode]

# run setup functions if modees have them
for mode_name in etc.mode_names :
    try :
        loading_banner("Loading " + str(mode_name) + ". Memory used: " + str(psutil.virtual_memory()[2]) )
        mode = sys.modules[mode_name]
        etc.mode_root = etc.MODES_PATH + mode_name + "/"
        print etc.mode_root
        mode.setup(screen, etc)
    except AttributeError :
        print "no setup found"
        continue 

filer.load_grabs()

buf = ''
line = ''
error = ''

count = 0
fps = 0
start = time.time()
clocker = pygame.time.Clock()

last_time = time.time()
this_time = 0

trig_last_time = time.time()
trig_this_time = 0


while 1:
    
    #check for OSC
    osc.recv()

    # get knobs from hardware or preset
    etc.update_knobs()

    # quit on esc
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()

    # measure FPS
    count += 1
    if ((count % 50) == 0):
        now = time.time()
        fps = 1 / ((now - start) / 50)
        start = now

    # check for sound
    sound.recv()

    if etc.refresh_mode:
        error = ''
        mode = sys.modules[etc.mode]

    if etc.clear_screen:
        screen.fill(etc.bg_color) 

    if etc.auto_clear :
        screen.fill(etc.bg_color) 

    etc.bg_color =  etc.color_picker_bg()
    
    # set mode
    #if etc.set_mode :
    #    error = ''
    #    print "setting: " + etc.mode
    #    try :
    #        etc.mode_root = MODES_PATH + etc.mode + "/"
    #        mode = sys.modules[etc.mode]
    #    except KeyError:
    #        error = "Module " +etc.mode+ " is not loaded, probably it has errors"

    # reload
    #if etc.reload_mode :
    #    error = ''
    #    # delete the old
    #    if etc.mode in sys.modules:  
    #        del(sys.modules[etc.mode]) 
    #    print "deleted module, reloading"
    #    mode_name = etc.mode
    #    mode_path = MODES_PATH+mode_name+'/main.py'
    #    try :
    #        mode = imp.load_source(mode_name, mode_path)
    #        print "reloaded"
            
            # then call setup
     #       try :
     #           etc.mode_root = MODES_PATH + mode_name + "/"
     #           mode.setup(screen, etc)
     #       except Exception, e:
     #           error = traceback.format_exc()
     #   except Exception, e:
     #       error = traceback.format_exc()
    
    try :
        mode.draw(screen, etc)
    except Exception, e:
        error = traceback.format_exc()
 
    #save frame
    if etc.screengrab:
        filenum = 0
        imagepath = etc.GRABS_PATH + str(filenum) + ".jpg"
        while os.path.isfile(imagepath):
            filenum += 1
            imagepath = etc.GRABS_PATH + str(filenum) + ".jpg"
        pygame.image.save(screen,imagepath)
        # add to the grabs array
        #grab = screen
        etc.grabindex += 1
        etc.grabindex %= 10
        pygame.transform.scale(screen, (128, 72), etc.tengrabs_thumbs[etc.grabindex] )
        etc.tengrabs[etc.grabindex] = screen.copy()
        print imagepath
   
    #draw the main screen, limit fps 30
    clocker.tick(30)
    hwscreen.blit(screen, (0,0))
    
    # osd
    if etc.osd :
        etc.ip = socket.gethostbyname(socket.gethostname())
        this_time = time.time()
        elapsed_time = this_time - last_time
        last_time = this_time
        osc_msgs_per_sec = osc_msgs_recv / elapsed_time
        #osd.fill(GREEN) 
        pygame.draw.rect(hwscreen, OSDBG, (0, hwscreen.get_height() - 40, hwscreen.get_width(), 40))
        font = pygame.font.SysFont(None, 32)
        #text = font.render(str(mode.__name__) + ', frame: ' + str(count) + ', fps: ' + str(int(fps)) + ', Auto Clear: ' + str(etc.auto_clear) + ', osc: ' + str(osc_msgs_recv) + ', osc / sec: ' + str(osc_msgs_per_sec), True, WHITE, OSDBG)
        text = font.render(str(mode.__name__) + ', frame: ' + str(count) + ', fps: ' + str(int(fps)) + ' IP: ' + str(etc.ip), True, WHITE, OSDBG)
        text_rect = text.get_rect()
        text_rect.x = 50
        text_rect.centery = hwscreen.get_height() - 20
        hwscreen.blit(text, text_rect)

        for i in range(0,10) :
            hwscreen.blit(etc.tengrabs_thumbs[i], (128 * i,0))

        # osd, errors
        i = 0
        for errorline in error.splitlines() :
            errormsg = font.render(errorline, True, WHITE, RED) 
            text_rect = notemsg.get_rect()
            text_rect.x = 50
            text_rect.y = 20 + (i * 32)
            hwscreen.blit(errormsg, text_rect)
            i += 1

    pygame.display.flip()

    if etc.quit :
        sys.exit()
    
    # clear all the events
    etc.clear_flags()
    osc_msgs_recv = 0

time.sleep(1)


print "Quit"

