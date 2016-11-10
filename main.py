import os
import pygame
import time
import random
import serial
import fullfb
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

def knobs_callback(path, args):
    global mvp
    k1, k2, k3, k4, k5, k6 = args
    
    mvp.knob1l = float(k4) / 1023
    mvp.knob2l = float(k1) / 1023
    mvp.knob3l = float(k2) / 1023
    mvp.knob4l = float(k5) / 1023
    mvp.knob5l = float(k3) / 1023
    #print mvp.knob5l   

    #print "received '%d'" % (k1)

def keys_callback(path, args) :
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

def midi_callback(path, args):
    global mvp
    n, v = args
    mvp.note_on = True
    mvp.note_num = n
    mvp.note_velocity = v

osc_server.add_method("/knobs", 'iiiiii', knobs_callback)
osc_server.add_method("/key", 'ii', keys_callback)
osc_server.add_method("/midi", 'ii', midi_callback)

#setup alsa for sound in

# Open the device in nonblocking capture mode. The last argument could
# just as well have been zero for blocking mode. Then we could have
# left out the sleep call in the bottom of the loop
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
#inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,0)

# Set attributes: Mono, 8000 Hz, 16 bit little endian samples
inp.setchannels(1)
inp.setrate(8000)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

# The period size controls the internal number of frames per period.
# The significance of this parameter is documented in the ALSA api.
# For our purposes, it is suficcient to know that reads from the device
# will return this many frames. Each frame being 2 bytes long.
# This means that the reads below will return either 320 bytes of data
# or 0 bytes of data. The latter is possible because we are in nonblocking
# mode.
inp.setperiodsize(300)

pygame.init()

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
OSDBG = (0,0,255)

# OSD stuff
font = pygame.font.SysFont(None, 32)
notemsg = font.render('...', True, WHITE, OSDBG)

# setup a UDP socket for recivinng data from other programs
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(0)

# TODO :  make helper module, include functions like these :
def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]


print "init serial port"
serialport = serial.Serial("/dev/ttymxc3", 500000)

print "opening frame buffer"
#screen = fullfb.init()
hwscreen = pygame.display.set_mode((1280,720),  pygame.FULLSCREEN | pygame.DOUBLEBUF, 32  )
screen = pygame.Surface(hwscreen.get_size())

# TODO :  don't make a list of moduels, just make a list of their names, and select them from  sys.modules
print "loading patches..."
patch_names = []
patch_folders = get_immediate_subdirectories('/usbdrive/Patches')

for patch_folder in patch_folders :
    patch_name = str(patch_folder)
    patch_path = '/usbdrive/Patches/'+patch_name+'/main.py'
    print patch_path
    try :
        imp.load_source(patch_name, patch_path)
        patch_names.append(patch_name)
    except Exception, e:
        print traceback.format_exc()

# set initial patch
num = 0
mvp.patch = patch_names[num]
patch = sys.modules[patch_names[num]]

# run setup functions if patches have them
# TODO: setup needs to get passed screen for things like setting sizes
for patch_name in patch_names :
    try :
        patch = sys.modules[patch_name]
        patch.setup(screen, mvp)
    except AttributeError :
        print "no setup found"
        continue 

# flush serial port
serialport.flushInput()

buf = ''
line = ''
error = ''

count = 0
fps = 0
start = time.time()
clocker = pygame.time.Clock()


while 1:
    
    #check for OSC
    while (osc_server.recv(1)):
        pass

    # get knobs from hardware or preset
    mvp.update_knobs()

    # quit on esc
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()



    #fps = count / (time.time() - start)
  
    
   # if ((count % 200) == 0):
    #`    mvp.next_patch = True        

    count += 1
    if ((count % 50) == 0):
        now = time.time()
        fps = 1 / ((now - start) / 50)
        start = now
        
    #if count > 1000:
    #    exit()
 

    # get audio
    # Read data from device
    l,data = inp.read()
    triggered = False
    while l:
        #print str(audioop.getsample(data, 2 ,0) )
        for i in range(0,100) :
            try :
                avg = audioop.getsample(data, 2, i * 3)
                avg += audioop.getsample(data, 2, (i * 3) + 1)
                avg += audioop.getsample(data, 2, (i * 3) + 2)
                #avg += audioop.getsample(data, 2, (i * 3) + 3)
                #avg += audioop.getsample(data, 2, (i * 4) + 3)
                avg = avg / 3
                if (avg > 1000) :
                    triggered = True
                #if (triggered) :
                mvp.audio_in[i] = avg
            except :
                pass
        l,data = inp.read()
    
        #print str(l)
        # Return the maximum of the absolute value of all samples in a fragment.
        #print audioop.max(data, 2)

   
    # get serial line and parse it, TODO hmmm could this miss lines?  (only parses most recent, but there could be more in serial buffer)
    if serialport.inWaiting() > 0:
        try:
            buf = buf + serialport.read(serialport.inWaiting())
            if '\n' in buf :
                lines = buf.split('\n')
                for l in lines :
                    mvp.parse_serial(l)
                buf = lines[-1]
        except: 
            pass

    # ... or parse lines from UDP instead
    try :
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        buf = buf + data
        if '\n' in buf :
            lines = buf.split('\n')
            for l in lines :
                mvp.parse_serial(l)
     #           print l
            buf = lines[-1]
    except :
        pass

    if mvp.next_patch: 
        num += 1
        if num == len(patch_names) : 
            num = 0
        mvp.patch = patch_names[num]
        patch = sys.modules[patch_names[num]]
    if mvp.prev_patch: 
        num -= 1
        if num < 0 : 
            num = len(patch_names) - 1
        mvp.patch = patch_names[num]
        patch = sys.modules[patch_names[num]]

#    if mvp.quarter_note : 
#        screen.fill ((0,0,0))
#        pygame.display.flip()

    #mvp.bg_color =  (mvp.knob5 / 4, mvp.knob5 % 256, (mvp.knob5 * 4) % 256)
    mvp.bg_color =  mvp.color_picker_bg()

    if mvp.clear_screen:
        #screen.fill( (random.randint(0,255), random.randint(0,255), random.randint(0,255))) 
        screen.fill(mvp.bg_color) 

    if mvp.auto_clear :
        screen.fill(mvp.bg_color) 

    #mvp.note_on = True

    # set patch
    if mvp.set_patch :
        print "setting: " + mvp.patch
        try :
            patch = sys.modules[mvp.patch]
            error = ''
        except KeyError:
            error = "Module " +mvp.patch+ " is not loaded, probably it has errors"

    # reload
    # TODO: setup has to be called too
    if mvp.reload_patch :
        # delete the old
        if mvp.patch in sys.modules:  
            del(sys.modules[mvp.patch]) 
        print "deleted module, reloading"
        patch_name = mvp.patch
        patch_path = '/usbdrive/Patches/'+patch_name+'/'+patch_name+'.py'
        try :
            patch = imp.load_source(patch_name, patch_path)
            error = ''
            print "reloaded"
            
            # then call setup
            try :
                patch.setup(screen, mvp)
                error = ''
            except Exception, e:
                error = traceback.format_exc()
        except Exception, e:
            error = traceback.format_exc()
          #  formatted_lines = traceback.format_exc().splitlines()
          #  print formatted_lines[-3]
          #  print formatted_lines[-1]
    
    try :
        patch.draw(screen, mvp)
        #error = ''
    except Exception, e:
        #print traceback.format_exc()
        error = traceback.format_exc()


    #save frame
    if mvp.screengrab:
        filenum = 0
        imagepath = "/usbdrive/Grabs" + str(filenum) + ".png"
        while os.path.isfile(imagepath):
            filenum += 1
            imagepath = "/usbdrive/Grabs" + str(filenum) + ".png"
        pygame.image.save(screen,imagepath)
        print imagepath
    
    # osd
    if mvp.osd :
        pygame.draw.rect(screen, OSDBG, (0, screen.get_height() - 40, screen.get_width(), 40))
        font = pygame.font.SysFont(None, 32)
        text = font.render(str(patch.__name__) + ', frame: ' + str(count) + ', fps: ' + str(int(fps)) + ', Auto Clear: ' + str(mvp.auto_clear), True, WHITE, OSDBG)
        text_rect = text.get_rect()
        text_rect.x = 50
        text_rect.centery = screen.get_height() - 20
        screen.blit(text, text_rect)
       
#        if mvp.note_on :
#            notemsg = font.render('note on', True, WHITE, OSDBG)
#        
#        text_rect = notemsg.get_rect()
#        text_rect.x = screen.get_width() - 100
#        text_rect.centery = screen.get_height() - 20
#        screen.blit(notemsg, text_rect)

        # osd, errors
        i = 0
        for errorline in error.splitlines() :
            errormsg = font.render(errorline, True, WHITE, RED) 
            text_rect = notemsg.get_rect()
            text_rect.x = 50
            text_rect.y = 20 + (i * 32)
            screen.blit(errormsg, text_rect)
            i += 1

       

    #clocker.tick(35)
    hwscreen.blit(screen, (0,0))
    pygame.display.flip()
    #time.sleep(.01)

    if mvp.quit :
        sys.exit()
    
    # clear all the events
    mvp.clear_flags()
    #time.sleep(.01)

time.sleep(1)


print "Quit"
