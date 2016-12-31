import os
import pygame
import time
import random
import glob
import etc_system
import imp
import socket
import traceback
import sys
import liblo
import psutil
from pygame.locals import *
import alsaaudio, audioop

GRABS_PATH = "/usbdrive/Grabs/"
MODES_PATH = "/usbdrive/Modes/"

#create etc object
etc = etc_system.System()
etc.clear_flags()

# get our ip
etc.ip = socket.gethostbyname(socket.gethostname())

# OSC init
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

osc_msgs_recv = 0

def fallback(path, args):
    global osc_msgs_recv
    osc_msgs_recv += 1

def knobs_callback(path, args):
    global osc_msgs_recv
    osc_msgs_recv += 1
    global etc
    k1, k2, k3, k4, k5, k6 = args
    etc.knob1l = float(k4) / 1023
    etc.knob2l = float(k1) / 1023
    etc.knob3l = float(k2) / 1023
    etc.knob4l = float(k5) / 1023
    etc.knob5l = float(k3) / 1023

def keys_callback(path, args) :
    global osc_msgs_recv
    osc_msgs_recv += 1
    global etc
    k, v = args
    if (k == 2 and v > 0) : etc.next_mode = True
    if (k == 1 and v > 0) : etc.prev_mode = True
    if (k == 9 and v > 0) : etc.clear_screen = True
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
    global osc_msgs_recv
    osc_msgs_recv += 1
    global etc
    c, n, v = args
    etc.note_on = True
    etc.note_num = n
    etc.note_velocity = v
    #print n

def midi_cc_callback(path, args):
    global osc_msgs_recv
    osc_msgs_recv += 1
    global etc
    c, n, v = args

    if n == 21 :
        etc.knob1l = float(v) / 127
    if n == 22 :
        etc.knob2l = float(v) / 127
    if n == 23 :
        etc.knob3l = float(v) / 127
    if n == 24 :
        etc.knob4l = float(v) / 127
    if n == 25 :
        etc.knob5l = float(v) / 127
#    print args


osc_server.add_method("/knobs", 'iiiiii', knobs_callback)
osc_server.add_method("/key", 'ii', keys_callback)
osc_server.add_method("/mnon", 'iii', midi_note_on_callback)
osc_server.add_method("/mcc", 'iii', midi_cc_callback)
osc_server.add_method(None, None, fallback)

#setup alsa for sound in
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
inp.setchannels(1)
inp.setrate(8000)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
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

# init fb and main surfaces
print "opening frame buffer"
hwscreen = pygame.display.set_mode((1280,720),  pygame.FULLSCREEN | pygame.DOUBLEBUF, 32  )
screen = pygame.Surface(hwscreen.get_size())
screen.fill((40,40,40)) 
hwscreen.blit(screen, (0,0))
pygame.display.flip()
hwscreen.blit(screen, (0,0))
pygame.display.flip()
liblo.send(osc_target, "/led", 7) # running
time.sleep(3)

# loading banner helper
def loading_banner(stuff) :
    global hwscreen
    screen.fill((40,40,40)) 
    font = pygame.font.SysFont(None, 40)
    text = font.render(stuff, True, WHITE, (40,40,40))
    text_rect = text.get_rect()
    text_rect.x = 20
    text_rect.y = 20
    hwscreen.blit(text, text_rect)
    pygame.display.flip()


# directory helper
def get_immediate_subdirectories(dir):
    if os.path.isdir(dir):
        return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]  
    else :
        return []

# load modes,  check if modes are found
print "loading modes..."
got_a_mode = False
mode_names = []
mode_folders = get_immediate_subdirectories(MODES_PATH)

for mode_folder in mode_folders :
    mode_name = str(mode_folder)
    mode_path = MODES_PATH+mode_name+'/main.py'
    print mode_path
    try :
        imp.load_source(mode_name, mode_path)
        got_a_mode = True
        mode_names.append(mode_name)
    except Exception, e:
        print traceback.format_exc()

#if not(os.path.isdir(MODES_PATH)) :
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
num = 0
etc.mode = mode_names[num]
mode = sys.modules[mode_names[num]]

# run setup functions if modees have them
for mode_name in mode_names :
    try :
        loading_banner("Loading " + str(mode_name) + ". Memory used: " + str(psutil.virtual_memory()[2]) )
        mode = sys.modules[mode_name]
        etc.mode_root = MODES_PATH + mode_name + "/"
        print etc.mode_root
        mode.setup(screen, etc)
    except AttributeError :
        print "no setup found"
        continue 

# recent grabs, first check if Grabs folder is available, create if not

if not(os.path.isdir(GRABS_PATH)) :
    print 'No grab folder, creating...'
    os.system('mkdir ' + GRABS_PATH)
print 'loading recent grabs...'
etc.tengrabs = []
etc.tengrabs_thumbs = []
etc.grabcount = 0
etc.grabindex = 0
for i in range(0,11):
    etc.tengrabs_thumbs.append(pygame.Surface((128, 72)))
    etc.tengrabs.append(pygame.Surface(hwscreen.get_size()))

for filepath in sorted(glob.glob(GRABS_PATH + '*.jpg')):
    filename = os.path.basename(filepath)
    print 'loading grab: ' + filename
    img = pygame.image.load(filepath)
    img = img.convert()
    thumb = pygame.transform.scale(img, (128, 72) )
    #TODO : ensure img is 1280 x 720, or does it matter?
    etc.tengrabs[etc.grabcount]= img
    etc.tengrabs_thumbs[etc.grabcount] = thumb
    etc.grabcount += 1
    if etc.grabcount > 10: break

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
    while (osc_server.recv(1)):
        pass
    #osc_server.recv(0)

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

    # get audio
    l,data = inp.read()
    etc.trig = False
    while l:
        for i in range(0,100) :
            try :
                avg = audioop.getsample(data, 2, i * 3)
                avg += audioop.getsample(data, 2, (i * 3) + 1)
                avg += audioop.getsample(data, 2, (i * 3) + 2)
                avg = avg / 3
                if (avg > 20000) :
                    trig_this_time = time.time()
                    if (trig_this_time - trig_last_time) > .05:
                        etc.trig = True
                        trig_last_time = trig_this_time
                etc.audio_in[i] = avg
            except :
                pass
        l,data = inp.read()

    # parse lines from UDP instead, this is from web
    try :
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        buf = buf + data
        if '\n' in buf :
            lines = buf.split('\n')
            for l in lines :
                etc.parse_serial(l)
            buf = lines[-1]
    except :
        pass

    if etc.next_mode: 
        error = ''
        num += 1
        if num == len(mode_names) : 
            num = 0
        etc.mode = mode_names[num]
        etc.mode_root = MODES_PATH + etc.mode + "/"
        mode = sys.modules[mode_names[num]]
    if etc.prev_mode: 
        error = ''
        num -= 1
        if num < 0 : 
            num = len(mode_names) - 1
        etc.mode = mode_names[num]
        etc.mode_root = MODES_PATH + etc.mode + "/"
        mode = sys.modules[mode_names[num]]

    if etc.clear_screen:
        screen.fill(etc.bg_color) 

    if etc.auto_clear :
        screen.fill(etc.bg_color) 

    etc.bg_color =  etc.color_picker_bg()
    
    # set mode
    if etc.set_mode :
        error = ''
        print "setting: " + etc.mode
        try :
            etc.mode_root = MODES_PATH + etc.mode + "/"
            mode = sys.modules[etc.mode]
        except KeyError:
            error = "Module " +etc.mode+ " is not loaded, probably it has errors"

    # reload
    if etc.reload_mode :
        error = ''
        # delete the old
        if etc.mode in sys.modules:  
            del(sys.modules[etc.mode]) 
        print "deleted module, reloading"
        mode_name = etc.mode
        mode_path = MODES_PATH+mode_name+'/main.py'
        try :
            mode = imp.load_source(mode_name, mode_path)
            print "reloaded"
            
            # then call setup
            try :
                etc.mode_root = MODES_PATH + mode_name + "/"
                mode.setup(screen, etc)
            except Exception, e:
                error = traceback.format_exc()
        except Exception, e:
            error = traceback.format_exc()
    
    try :
        etc.mode_root = MODES_PATH + mode_name + "/"
        mode.draw(screen, etc)
    except Exception, e:
        error = traceback.format_exc()
 
    #save frame
    if etc.screengrab:
        filenum = 0
        imagepath = GRABS_PATH + str(filenum) + ".jpg"
        imagepath_thumb = GRABS_PATH + str(filenum) + "_thumb.jpg"
        while os.path.isfile(imagepath):
            filenum += 1
            imagepath = GRABS_PATH + str(filenum) + ".jpg"
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
