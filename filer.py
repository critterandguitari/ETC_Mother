import glob
import os
import pygame
import traceback
import imp

etc = None

def init (etc_object) :
    global etc
    etc = etc_object 

def get_immediate_subdirectories(dir):
    if os.path.isdir(dir):
        return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]  
    else :
        return []

# save a screenshot
def screengrab(screen):
    global etc
    filenum = 0
    imagepath = etc.GRABS_PATH + str(filenum) + ".jpg"
    while os.path.isfile(imagepath):
        filenum += 1
        imagepath = etc.GRABS_PATH + str(filenum) + ".jpg"
    pygame.image.save(screen,imagepath)
    # add to the grabs array
    etc.grabindex += 1
    etc.grabindex %= 10
    pygame.transform.scale(screen, (128, 72), etc.tengrabs_thumbs[etc.grabindex] )
    etc.tengrabs[etc.grabindex] = screen.copy()
    print "grabbed " + imagepath


# load modes,  check if modes are found
def load_modes():
    global etc
    print "loading modes..."
    got_a_mode = False # at least one mode
    mode_folders = get_immediate_subdirectories(etc.MODES_PATH)

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
    
    return got_a_mode

# recent grabs, first check if Grabs folder is available, create if not
def load_grabs():
    if not(os.path.isdir(etc.GRABS_PATH)) :
        print 'No grab folder, creating...'
        os.system('mkdir ' + etc.GRABS_PATH)
    print 'loading recent grabs...'
    etc.tengrabs = []
    etc.tengrabs_thumbs = []
    etc.grabcount = 0
    etc.grabindex = 0
    for i in range(0,11):
        etc.tengrabs_thumbs.append(pygame.Surface((128, 72)))
        etc.tengrabs.append(pygame.Surface(etc.RES ))

    for filepath in sorted(glob.glob(etc.GRABS_PATH + '*.jpg')):
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

