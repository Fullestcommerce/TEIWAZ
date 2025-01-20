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
    world = load_world()
    world_rect=world.get_rect()
    actor, actor_rect = create_actor()
    target=None

    running=True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                target=event.pos
        target = move_actor(actor_rect, target)

        screen.fill((0, 0, 0))
        screen.blit(world, world_rect)
        screen.blit(actor, actor_rect)

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