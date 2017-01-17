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
#    etc.ip = socket.gethostbyname(socket.gethostname())
    pygame.draw.rect(screen, etc.OSDBG, (0, screen.get_height() - 40, screen.get_width(), 40))
    font = pygame.font.SysFont(None, 32)
    text = font.render(str(etc.mode) + ', frame: ' + str(etc.frame_count) + ', fps: ' + str(int(etc.fps)) + ' IP: ' + str(etc.ip), True, etc.WHITE, etc.OSDBG)
    text_rect = text.get_rect()
    text_rect.x = 50
    text_rect.centery = screen.get_height() - 20
    screen.blit(text, text_rect)

    for i in range(0,10) :
        screen.blit(etc.tengrabs_thumbs[i], (128 * i,0))

    # osd, errors
    i = 0
    for errorline in etc.error.splitlines() :
        errormsg = font.render(errorline, True, etc.WHITE, etc.RED) 
        text_rect.x = 50
        text_rect.y = 20 + (i * 32)
        screen.blit(errormsg, text_rect)
        i += 1


