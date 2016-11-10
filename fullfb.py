import os
import pygame

screen = None;

def init():
    "Ininitializes a new pygame screen using the framebuffer"
    # Based on "Python GUI in Linux frame buffer"
    # http://www.karoltomala.com/blog/?p=679
    disp_no = os.getenv("DISPLAY")
    if disp_no:
        print "I'm running under X display = {0}".format(disp_no)
    
    # Check which frame buffer drivers are available
    # Start with fbcon since directfb hangs with composite output
    #drivers = ['fbcon', 'directfb', 'svgalib']
    #drivers = ['directfb', 'svgalib']
    drivers = ['vesafbdf']
    found = False
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            print 'Driver: {0} '.format(driver)
            pygame.display.init()
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit()
            continue
        found = True
        break

    if not found:
        raise Exception('No suitable video driver found!')
    
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print "Framebuffer size: %d x %d" % (size[0], size[1])
    
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    #screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
    #screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.DOUBLEBUF)
    #screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.HWSURFACE)


    # Clear the screen to start
    screen.fill((255, 105, 180))        
    # Initialise font support
    pygame.font.init()
    # Render the screen
    pygame.display.update()
    return screen

