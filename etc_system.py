import fileinput
import random
import math
import pygame
import traceback
import imp
import os
import glob
import sys
import helpers

class System:

    GRABS_PATH = "/usbdrive/Grabs/"
    MODES_PATH = "/usbdrive/Modes/"

    RES =  (1280,720)

    # this is just an alias to the screen in main loop
    screen = None

    fps = 0
    frame_count = 0

    # some colors we use
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    OSDBG = (0,0,255)

    # screen grabs
    tengrabs = []
    tengrabs_thumbs = []
    grabcount = 0
    grabindex = 0
    
    # modes
    mode_names = []
    mode_index = 0
    mode = ''
    mode_root = ''
    error = ''
    run_setup = False
    
    # audio
    audio_in = [0] * 100
    trig = False
    
    # knobs a used by mode 
    knob1 = .200
    knob2 = .200
    knob3 = .200
    knob4 = .200
    knob5 = .200
   
    # knob values used internally
    knob = [.2] * 5
    knob_snapshot = [.2] * 5
    knob_override = [False] * 5

    # midi stuff (CC gets updated into knobs
    notes = [0] * 128
    midi_pgm = 0
    midi_clk = 0

    # system stuff 
    ip = ''
    auto_clear = True
    bg_color = (0, 0, 0)
    quit = False
    osd = False

    def set_mode_by_name (self, new_mode) :
        pass

    def set_mode_by_index (self, index) :
        self.mode_index = index
        self.mode = self.mode_names[self.mode_index]
        self.mode_root = self.MODES_PATH + self.mode + "/"
        self.error = ''

    def set_mode_by_name (self, name) :
        self.mode = name #self.mode_names[self.mode_index]
        self.mode_index = self.mode_names.index(name)
        self.mode_root = self.MODES_PATH + self.mode + "/"
        self.error = ''

    def next_mode (self) :
        self.mode_index += 1
        if self.mode_index == len(self.mode_names) : 
            self.mode_index = 0
        self.set_mode_by_index(self.mode_index)

    def prev_mode (self) :
        self.mode_index -= 1
        if self.mode_index <= 0 : 
            self.mode_index = len(self.mode_names) - 1
        self.set_mode_by_index(self.mode_index)

    def update_knob (self, index, val) :
        if self.knob_override[index] :
            if abs(self.knob_snapshot[index] - val) > .05 :
                self.knob_override[index] = False
                self.knob[index] = val
        else : 
            self.knob[index] = val

    # then do this for the modes 
    def update_knobs(self) :
        self.knob1 = self.knob[0]
        self.knob2 = self.knob[1]
        self.knob3 = self.knob[2]
        self.knob4 = self.knob[3]
        self.knob5 = self.knob[4]

    # save a screenshot
    def screengrab(self):
        filenum = 0
        imagepath = self.GRABS_PATH + str(filenum) + ".jpg"
        while os.path.isfile(imagepath):
            filenum += 1
            imagepath = self.GRABS_PATH + str(filenum) + ".jpg"
        pygame.image.save(self.screen,imagepath)
        # add to the grabs array
        self.grabindex += 1
        self.grabindex %= 10
        pygame.transform.scale(self.screen, (128, 72), self.tengrabs_thumbs[self.grabindex] )
        self.tengrabs[self.grabindex] = self.screen.copy()
        print "grabbed " + imagepath

    # load modes,  check if modes are found
    def load_modes(self):
        print "loading modes..."
        got_a_mode = False # at least one mode
        mode_folders = helpers.get_immediate_subdirectories(self.MODES_PATH)

        for mode_folder in mode_folders :
            mode_name = str(mode_folder)
            mode_path = self.MODES_PATH+mode_name+'/main.py'
            print mode_path
            try :
                imp.load_source(mode_name, mode_path)
                self.mode_names.append(mode_name)
                got_a_mode = True
            except Exception, e:
                print traceback.format_exc()
        return got_a_mode
 
    # reload mode module
    def reload_mode(self) :
        # delete the old, and reload
        if self.mode in sys.modules:  
            del(sys.modules[self.mode]) 
        print "deleted module, reloading"
        try :
            imp.load_source(self.mode, self.mode_root+'/main.py')
            print "reloaded"
            # then call setup
        except Exception, e:
            self.error = traceback.format_exc()
            print "error reloading: " + self.error
        self.run_setup = True # set a flag so setup gets run from main loop
    
    # recent grabs, first check if Grabs folder is available, create if not
    def load_grabs(self):
        if not(os.path.isdir(self.GRABS_PATH)) :
            print 'No grab folder, creating...'
            os.system('mkdir ' + self.GRABS_PATH)
        print 'loading recent grabs...'
        self.tengrabs = []
        self.tengrabs_thumbs = []
        self.grabcount = 0
        self.grabindex = 0
        for i in range(0,11):
            self.tengrabs_thumbs.append(pygame.Surface((128, 72)))
            self.tengrabs.append(pygame.Surface(self.RES ))

        for filepath in sorted(glob.glob(self.GRABS_PATH + '*.jpg')):
            filename = os.path.basename(filepath)
            print 'loading grab: ' + filename
            img = pygame.image.load(filepath)
            img = img.convert()
            thumb = pygame.transform.scale(img, (128, 72) )
            #TODO : ensure img is 1280 x 720, or does it matter?
            self.tengrabs[self.grabcount]= img
            self.tengrabs_thumbs[self.grabcount] = thumb
            self.grabcount += 1
            if self.grabcount > 10: break

    def color_picker( self ):
        # convert knob to 0-1
        c = float(self.knob4)

        # all the way down random bw
        rando = random.randrange(0, 2)
        color = (rando * 255, rando * 255, rando * 255)

        # random greys
        if c > .02 :
            rando = random.randrange(0,255)
            color = (rando, rando, rando)
        # grey 1
        if c > .04 :
            color = (50, 50, 50)
        # grey 2
        if c > .06 :
            color = (100, 100 ,100)
        # grey 3
        if c > .08 :
            color = (150, 150 ,150)
        # grey 4
        if c > .10 :
            color = (150, 150 ,150)
            
        # grey 5
        if c > .12 :
            color = (200, 200 ,200)
        # white
        if c > .14 :
            color = (250, 250 ,250)
        #colors
        if c > .16 :
            
            #r = float(control) / 1024 * 255
            #g = float((control * 2) % 1024) / 1024 * 255
            #b = float((control * 4) % 1024) / 1024 * 255
            
            r = math.sin(c * 2 * math.pi) * .5 + .5
            g = math.sin(c * 4 * math.pi) * .5 + .5
            b = math.sin(c * 8 * math.pi) * .5 + .5
            color = (r * 255,g * 255,b * 255)
        # full ranoms
        if c > .96 :
            color = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
        # primary randoms
        if c > .98 :
            r = random.randrange(0, 2) * 255
            g = random.randrange(0, 2) * 255
            b = random.randrange(0, 2) * 255
            color = (r,g,b)
        
        color2 = (color[0], color[1], color[2])
        return color2
 
    def color_picker_bg( self ):
        c = self.knob5
        # all the way down random bw
        rando = random.randrange(0, 2)
        color = (rando * 255, rando * 255, rando * 255)

        # random greys
        if c > .02 :
            rando = random.randrange(0,255)
            color = (rando, rando, rando)
        # grey 1
        if c > .04 :
            color = (50, 50, 50)
        # grey 2
        if c > .06 :
            color = (100, 100 ,100)
        # grey 3
        if c > .08 :
            color = (150, 150 ,150)
        # grey 4
        if c > .10 :
            color = (150, 150 ,150)
            
        # grey 5
        if c > .12 :
            color = (200, 200 ,200)
        # white
        if c > .14 :
            color = (250, 250 ,250)
        #colors
        if c > .16 :
            r = math.sin(c * 2 * math.pi) * .5 + .5
            g = math.sin(c * 4 * math.pi) * .5 + .5
            b = math.sin(c * 8 * math.pi) * .5 + .5
            color = (r * 255,g * 255,b * 255)
        # full ranoms
        if c > .96 :
            color = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
        # primary randoms
        if c > .98 :
            r = random.randrange(0, 2) * 255
            g = random.randrange(0, 2) * 255
            b = random.randrange(0, 2) * 255
            color = (r,g,b)
        
        self.bg_color = color
        return color
 
    def save_preset(self):
        print "saving preset"
        fo = open("/usbdrive/presets.txt", "a+")
        fo.write(self.mode + "," + str(self.knob1) + "," + str(self.knob2) +"," + str(self.knob3) + "," + str(self.knob4) +  "," + str(self.knob5) + "," + str(self.auto_clear) + "\n");
        fo.close()

    def next_preset(self):
        presets = []
        for line in fileinput.input("/usbdrive/presets.txt"):
            presets.append(line)
        self.preset_index += 1
        if self.preset_index == len(presets):
            self.preset_index = 0
        self.recall_preset(presets[self.preset_index])

    def prev_preset(self):
        presets = []
        for line in fileinput.input("/usbdrive/presets.txt"):
            presets.append(line)
        self.preset_index -= 1
        if self.preset_index < 0:
            self.preset_index = len(presets) - 1
        self.recall_preset(presets[self.preset_index])

    def recall_preset(self, preset) :
        array = preset.strip().split(',')
        if len(array) == 7 :
            print "recalling preset: " + str(preset)
            self.mode = array[0]
            # snapshot current knobs
            self.knob1s = self.knob1l 
            self.knob2s = self.knob2l
            self.knob3s = self.knob3l
            self.knob4s = self.knob4l 
            self.knob5s = self.knob5l 

            # then lock em, if they locked we'll use the preset value
            self.knob1lock = self.knob2lock = self.knob3lock = self.knob4lock = self.knob5lock = True
            if str(array[6]) == "False":
                self.auto_clear = False
            else :
                self.auto_clear = True
            self.set_mode = True

    def clear_flags(self):
        self.trig = False
        self.run_setup = False


