#main game file
import pygame
import sys
from menu import main_menu
from logic import *
pygame.init()
    #screen parameters and version
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("TEIWAZ v_0.1")
    #FPS
clock = pygame.time.Clock()
FPS=24
    #loop
def main_loop():
    world = create_world()
    actor=pygame.image.load("assets/actor.png")
    actor_rect=actor.get_rect()
    actor_pos=[0,0]#screen center
    target=[400,300]

    running=True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                target=event.pos
        
        target = move_actor(actor_pos, target, world)
        print(target)

        camera_x = actor_pos[0] #- screen.get_width() // 2 
        camera_y = actor_pos[1] #- screen.get_height() // 2
            
        #camera_x = max(0, min(camera_x, MAP_WIDTH * TILE_SIZE - screen.get_width())) 
        #camera_y = max(0, min(camera_y, MAP_HEIGHT * TILE_SIZE - screen.get_height()))
        screen.fill((0, 0, 0))
        render_world(screen, world, camera_x, camera_y)
        screen.blit(actor, (screen.get_width() // 2 - actor_rect.width // 2, screen.get_height() // 2 - actor_rect.height // 2))
        if target:
            pygame.draw.circle(screen, (0, 255, 0), (target[0], target[1]), 5)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__=="__main__":
    act=main_menu(screen, clock, FPS)
    if act == "launch_game":
        main_loop()
    pygame.quit()
    sys.exit()