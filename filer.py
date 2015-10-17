import glob
import os
import pygame

etc = None

def init (etc_object) :
    global inp, etc
    etc = etc_object 

def get_immediate_subdirectories(dir):
    if os.path.isdir(dir):
        return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]  
    else :
        return []

def load_grabs():
# recent grabs, first check if Grabs folder is available, create if not
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

