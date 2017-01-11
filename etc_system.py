import fileinput
import random
import math

class System:

    GRABS_PATH = "/usbdrive/Grabs/"
    MODES_PATH = "/usbdrive/Modes/"

    RES =  (1280,720)
    
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
    refresh_mode = False
    error = ''
    
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
    screengrab = False
    auto_clear = True
    bg_color = (0, 0, 0)
    quit = False
    osd = False
    reload_mode = False

    def set_mode_by_name (self, new_mode) :
        pass

    def set_mode_by_index (self, index) :
        self.mode_index = index
        self.mode = self.mode_names[self.mode_index]
        self.mode_root = self.MODES_PATH + self.mode + "/"
        self.refresh_mode = True

    def set_mode_by_name (self, name) :
        self.mode = name #self.mode_names[self.mode_index]
        self.mode_index = self.mode_names.index(name)
        self.mode_root = self.MODES_PATH + self.mode + "/"
        self.refresh_mode = True

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
        self.clear_screen = False
        self.note_on = False
        self.note_off = False
        self.quarter_note = False
        self.eighth_note = False
        self.eighth_note_triplet = False
        self.sixteenth_note = False
        self.thirtysecond_note = False
        self.half_note = False
        self.whole_note = False
        self.set_mode = False
        self.reload_mode = False
        self.aux_button = False
        self.screengrab = False
        self.trig = False
        self.refresh_mode = False


