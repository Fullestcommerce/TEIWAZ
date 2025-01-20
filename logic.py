import pygame
#world map
def load_world():
    world_map = pygame.image.load("assets/background.png")
    return world_map

def create_actor():
    actor = pygame.image.load("assets/actor.png")
    actor_rect = actor.get_rect()
    actor_rect.center = (400, 300)  # Початкова позиція на екрані
    return actor, actor_rect

def move_actor(actor_rect, target):
    if target:
        dx = target[0] - actor_rect.centerx
        dy = target[1] - actor_rect.centery
        distance = (dx**2 + dy**2) ** 0.5
        if distance < 5:
            target = None
        else:
            actor_rect.centerx += dx / distance * 5
            actor_rect.centery += dy / distance * 5
    return target
