import pygame
import random
TILE_SIZE=32
MAP_WIDTH=50
MAP_HEIGHT=50
#world map
def create_world():
    world_map = [] 
    for x in range(MAP_WIDTH): 
        column = [] 
        for y in range(MAP_HEIGHT): 
            terrain_difficulty = random.randint(1, 5) 
            column.append(terrain_difficulty)
        world_map.append(column)
    return world_map
def render_world(screen, world_map, camera_x, camera_y):
    for x in range(MAP_WIDTH): 
        for y in range(MAP_HEIGHT): 
            tile_color = (world_map[x][y] * 50, world_map[x][y] * 50, world_map[x][y] * 50) 
            pygame.draw.rect(screen, tile_color, (x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE))

def move_actor(actor_pos, target, world_map):
    if target:
        dx = target[0]-400
        dy = target[1]-300
        print(dx, dy)
        distance = (dx**2 + dy**2) ** 0.5
        if distance < 5:
            target = [400,300]
        else:
            x, y = actor_pos[0]//TILE_SIZE, actor_pos[1]//TILE_SIZE
            speed=min(5/world_map[int(x)][int(y)],5)
            actor_pos[0] += dx / distance * speed
            actor_pos[1] += dy / distance * speed
            target=list(target)
            target[0] -= dx/distance * speed
            target[1] -= dy / distance * speed
            print(f"Actor pos: {actor_pos}, Speed: {speed}, Distance: {distance}")
    return target
