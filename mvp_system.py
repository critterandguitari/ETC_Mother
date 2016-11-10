import fileinput
import random
import math

class System:

    # TODO  fix this knob shit up

    # knobs used by patch (either preset or live)
    knob1 = .200
    knob2 = .200
    knob3 = .200
    knob4 = .200
    knob5 = .200

    # live knobs vals
    knob1l = .200
    knob2l = .200
    knob3l = .200
    knob4l = .200
    knob5l = .200

    # snapshot of live knobs
    knob1s = .200
    knob2s = .200
    knob3s = .200
    knob4s = .200
    knob5s = .200

    # preset knob vals
    knob1s = .200
    knob2s = .200
    knob3s = .200
    knob4s = .200
    knob5s = .200

    # if a knob is locked
    knob1lock = False
    knob2lock = False
    knob3lock = False
    knob4lock = False
    knob5lock = False


    clear_screen = False
    midi_clk = False
    midi_start = False
    midi_stop = False
    midi_clk_count = 0
    
    audio_in = [0] * 100

    quarter_note = False
    eighth_note = False
    eighth_note_triplet = False
    sixteenth_note = False
    thirtysecond_note = False

    half_note = False
    whole_note = False

    midi_clk_count = 0
    whole_note_count = 0

    note_on = False
    note_off = False
    note_ch = 1
    note_velocity = 0
    note_num = 60

    aux_button = False
    screengrab = False
    auto_clear = True

    bg_color = (0, 0, 0)

    next_patch = False
    prev_patch = False
    set_patch = False
    reload_patch = False
    patch = ''
    
    preset_index = 0

    quit = False

    osd = False
  
    brightness = 1
   
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
        
        color2 = (color[0] * self.brightness, color[1] * self.brightness, color[2] * self.brightness)
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
        
        return color
 



    def parse_serial(self, line):
        array = line.split(',')
        #print array
        if len (array) == 1:
            if array[0] == "aux": 
                self.aux_button = True
  
        if len (array) == 1:
            if array[0] == "osd": 
                if self.osd :
                    self.osd = False
                else :
                    self.osd = True
  
        if len (array) == 1:
            if array[0] == "quit": 
                self.quit = True
  
        if len (array) == 1:
            if array[0] == "sd": 
                self.quit = True
  
        if len (array) == 1:
            if array[0] == "rst": 
                self.reload_patch = True
   
        if len (array) == 1:
            if array[0] == "rlp": 
                self.reload_patch = True
 
        if len (array) == 1:
            if array[0] == "cs": 
                self.clear_screen = True
  
        if len (array) == 1:
            if array[0] == "screengrab": 
                self.screengrab = True

        # basic parse sd key (this is supposed to be mapped to shutdowh -h now)
        if len (array) == 1:
            if array[0] == "sd": 
                self.clear_screen = True
      
        if len(array) == 1:
            if array[0] == "np" :
                print 'np'
                self.next_patch = True
       
        if len(array) == 1:
            if array[0] == "pp" :
                print 'pp'
                self.prev_patch = True
   
        if len(array) == 1:
            if array[0] == "spre" :
                self.save_preset()
 
        if len(array) == 1:
            if array[0] == "npre" :
                self.next_preset()
 
        if len(array) == 1:
            if array[0] == "ppre" :
                self.prev_preset()
 


        # basic midi start
        if len(array) == 1:
            if array[0] == "ms" :
                self.midi_start = True
                self.midi_clk_count = 0
                self.whole_note_count = 0
        
        # basic midi syn
        if len(array) == 1:
            if array[0] == "my" :
#                print self.midi_clk_count
                self.clk = True
                
                if self.whole_note_count == 0: self.whole_note = True
                if (self.whole_note_count % 48) == 0: self.half_note = True

                if self.midi_clk_count == 0 : self.quarter_note = True
                if (self.midi_clk_count % 12) == 0 : self.eighth_note = True
                if (self.midi_clk_count % 8) == 0 : self.eighth_note_triplet = True
                if (self.midi_clk_count % 6) == 0 : self.sixteenth_note = True
                if (self.midi_clk_count % 3) == 0 : self.thirty_triplet = True

                self.midi_clk_count += 1
                if self.midi_clk_count == 24 : self.midi_clk_count = 0

                self.whole_note_count += 1
                if self.whole_note_count == 96 : self.midi_clk_count = 0

        if len(array) == 2 :
            if array[0] == "setpatch" :
                self.set_patch = True
                self.patch = array[1]


        # basic parse of knob array
        if len(array) == 5 :
            if array[0] == "k" :
                if array[1].isdigit() :
                    self.knob1 = int(array[1])
                if array[2].isdigit() :
                    self.knob2 = int(array[2])
                if array[3].isdigit() :
                    self.knob3 = int(array[3])
                if array[4].isdigit() :
                    self.knob4 = int(array[4])
      
        # basic parse note on command
        if len(array) == 4:
            if array[0] == "no" :
                self.note_on = True
                if array[1].isdigit() :
                    self.note_ch = int(array[1])
                if array[2].isdigit() :
                    self.note_note = int(array[2])
                if array[3].isdigit() :
                    self.note_velocity = int(array[3])
 
        # basic parse note off command
        if len(array) == 4:
            if array[0] == "nf" :
                self.note_off = True
                if array[1].isdigit() :
                    self.note_ch = int(array[1])
                if array[2].isdigit() :
                    self.note_note = int(array[2])
                if array[3].isdigit() :
                    self.note_velocity = int(array[3])

 


    def save_preset(self):
        print "saving preset"
        fo = open("../presets.txt", "a+")
        fo.write(self.patch + "," + str(self.knob1) + "," + str(self.knob2) +"," + str(self.knob3) + "," + str(self.knob4) +  "," + str(self.knob5) + "," + str(self.auto_clear) + "\n");
        fo.close()

    def next_preset(self):
        presets = []
        for line in fileinput.input("../presets.txt"):
            presets.append(line)
        self.preset_index += 1
        if self.preset_index == len(presets):
            self.preset_index = 0
        self.recall_preset(presets[self.preset_index])

    def prev_preset(self):
        presets = []
        for line in fileinput.input("../presets.txt"):
            presets.append(line)
        self.preset_index -= 1
        if self.preset_index < 0:
            self.preset_index = len(presets) - 1
        self.recall_preset(presets[self.preset_index])

    def recall_preset(self, preset) :
        array = preset.strip().split(',')
        if len(array) == 7 :
            print "recalling preset: " + str(preset)
            self.patch = array[0]
            # snapshot current knobs
            self.knob1s = self.knob1l 
            self.knob2s = self.knob2l
            self.knob3s = self.knob3l
            self.knob4s = self.knob4l 
            self.knob5s = self.knob5l 
            
            # update preset vals
            self.knob1p = float(array[1])
            self.knob2p = float(array[2])
            self.knob3p = float(array[3])
            self.knob4p = float(array[4])
            self.knob5p = float(array[5])

            # then lock em, if they locked we'll use the preset value
            self.knob1lock = self.knob2lock = self.knob3lock = self.knob4lock = self.knob5lock = True
            if str(array[6]) == "False":
                self.auto_clear = False
            else :
                self.auto_clear = True
            self.set_patch = True


    # TODO  fix this,  what the hell!!!!
    def update_knobs(self) :
        if self.knob1lock :
            if abs(self.knob1s - self.knob1l) > .05 :
                self.knob1lock = False
                self.knob1 = self.knob1l
            else : 
                self.knob1 = self.knob1p
        else :
            self.knob1 = self.knob1l
        if self.knob2lock :
            if abs(self.knob2s - self.knob2l) > .05 :
                self.knob2lock = False
                self.knob2 = self.knob2l
            else : 
                self.knob2 = self.knob2p
        else :
            self.knob2 = self.knob2l
        if self.knob3lock :
            if abs(self.knob3s - self.knob3l) > .05 :
                self.knob3lock = False
                self.knob3 = self.knob3l
            else : 
                self.knob3 = self.knob3p
        else :
            self.knob3 = self.knob3l
        if self.knob4lock :
            if abs(self.knob4s - self.knob4l) > .05 :
                self.knob4lock = False
                self.knob4 = self.knob4l
            else : 
                self.knob4 = self.knob4p
        else :
            self.knob4 = self.knob4l
        if self.knob5lock :
            if abs(self.knob5s - self.knob5l) > .05 :
                self.knob5lock = False
                self.knob5 = self.knob5l
            else : 
                self.knob5 = self.knob5p
        else :
            self.knob5 = self.knob5l

    def clear_flags(self):
        self.next_patch = False
        self.prev_patch = False
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
        self.next_patch = False
        self.set_patch = False
        self.reload_patch = False
        self.aux_button = False
        self.screengrab = False



