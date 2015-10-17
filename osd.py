import pygame
import socket

etc = None

def init(etc_obj) :
    global etc
    etc = etc_obj

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

    pygame.draw.rect(screen, etc.BLACK, (0, screen.get_height() - 90, screen.get_width(), 90))
    font = pygame.font.Font("Avenir-Medium.ttf", 32)
    
    mode_str = " Mode: " + str(etc.mode_index) + "/" + str(len(etc.mode_names)) + ", "  + str(etc.mode) + " " 
    scene_str = " Scene: Not Set" + " "
    fps_str = " FPS: " + str(int(etc.fps)) + " "
    ip_str = " IP: " + str(etc.ip) + " "
    auto_clr_str = " Auto Clear: " + str(etc.auto_clear) + " " 

    text = font.render(mode_str + "   " + scene_str + "   " + fps_str, True, etc.WHITE, etc.BLACK)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = screen.get_height() - 65
    

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


