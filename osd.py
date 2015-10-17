import pygame
import socket

etc = None

def init(etc_obj) :
    global etc
    etc = etc_obj

def draw_knob_slider(screen, etc, offx, offy, index) :
    if etc.knob_override[index]:
        color = etc.RED
    else :
        color = etc.WHITE
    pygame.draw.line(screen, color, [offx, offy], [offx + 16, offy], 1)
    pygame.draw.line(screen, color, [offx, offy], [offx, offy + 40], 1)
    pygame.draw.line(screen, color, [offx + 16, offy], [offx + 16, offy + 40], 1)
    pygame.draw.line(screen, color, [offx, offy + 40], [offx + 16, offy + 40], 1)
    pygame.draw.rect(screen, color, (offx, offy + 40 - int(40*etc.knob[index]), 16, int(40*etc.knob[index])))

# loading banner helper
def loading_banner(screen, stuff) :
    global etc
    screen.fill((0,0,0)) 
        
    font = pygame.font.Font("./Avenir-Medium.ttf", 150)
    text = font.render("ETC", True, (255,255,255))
    textpos = text.get_rect()
    textpos.centerx = screen.get_width() / 2
    textpos.centery = screen.get_height() /2
    screen.blit(text, textpos)

    font = pygame.font.Font("./Avenir-Medium.ttf", 32)
    text = font.render(stuff, True, (255,255,255))
    text_rect = text.get_rect()
    text_rect.x = 20
    text_rect.y = 650
    screen.blit(text, text_rect)
    pygame.display.flip()

# main screen osd
def render_overlay(screen) :
    global etc

    font = pygame.font.Font("Avenir-Medium.ttf", 32)

    
    # mode
    #mode_str = "Mode: " + str(etc.mode_index) + "/" + str(len(etc.mode_names)) + ", "  + str(etc.mode) 
    mode_str = " Mode:  "   + str(etc.mode) + " "
    text = font.render(mode_str, True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = 200
    screen.blit(text, text_rect)
    
    # scene
    if etc.scene_set :
        scene_str = " Scene:  " + str(etc.scene_index) +" of "+str(len(etc.scenes)) + " "
    else:
        scene_str = " Scene: Not Set "
    text = font.render(scene_str, True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = 253
    screen.blit(text, text_rect)   
        
    
    fps_str = "FPS: " + str(int(etc.fps))
   # text = font.render(mode_str + "   " + scene_str + "   " + fps_str, True, etc.WHITE, etc.BLACK)


    
    # midi notes
    pygame.draw.rect(screen, etc.BLACK, (50, 285, 530, 55))
    text = font.render(" MIDI Notes:", True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = 314
    screen.blit(text, text_rect)  
    offx = 250
    offy = 292
    for i in range(0, 33):
        pygame.draw.line(screen, etc.WHITE, [(i*10)+offx, offy], [(i*10)+offx, 40+offy], 1)
    for i in range(0, 5):
        pygame.draw.line(screen, etc.WHITE, [offx, (i*10)+offy], [offx + 320, (i*10)+offy], 1)
    for i in range(0,128):
        if (etc.notes[i] > 0):
            pygame.draw.rect(screen, etc.WHITE, (offx + 10 * (i % 32), offy + 10 * (i / 32), 10, 10))
            
    # knobs
    pygame.draw.rect(screen, etc.BLACK, (50, 355, 228, 55))
    text = font.render(" Knobs:", True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = 385
    screen.blit(text, text_rect)
    draw_knob_slider(screen, etc, 170, 362, 0)
    draw_knob_slider(screen, etc, 190, 362, 1)
    draw_knob_slider(screen, etc, 210, 362, 2)
    draw_knob_slider(screen, etc, 230, 362, 3)
    draw_knob_slider(screen, etc, 250, 362, 4)
    
    # trigger
    pygame.draw.rect(screen, etc.BLACK, (50, 420, 175, 45))
    text = font.render(" Trigger:", True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = 440
    screen.blit(text, text_rect)
    pygame.draw.rect(screen, etc.WHITE, (180, 425, 40, 35), 1)
    if etc.trig:
        print "t"
        pygame.draw.rect(screen, etc.GREEN, (180, 425, 40, 35))
    
    # ip    
    mode_str = " IP Address:  "   + str(etc.ip) + " "
    text = font.render(mode_str, True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = 500
    screen.blit(text, text_rect)
    
        # ip    
    mode_str = " Memory:  "   + str(etc.ip) + " "
    text = font.render(mode_str, True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = 555
    screen.blit(text, text_rect)

    for i in range(0,10) :
        screen.blit(etc.tengrabs_thumbs[i], (128 * i,0))

    # osd, errors
    i = 0
    font = pygame.font.Font("Avenir-Medium.ttf", 24)
    for errorline in etc.error.splitlines() :
        errormsg = font.render(errorline, True, etc.WHITE, etc.RED) 
        text_rect.x = 50
        text_rect.y = 100 + (i * 32)
        screen.blit(errormsg, text_rect)
        i += 1


