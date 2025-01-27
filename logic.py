import pygame
import random
from noise import pnoise2
TILE_SIZE=32
MAP_WIDTH=300 
MAP_HEIGHT=300
SCALE=100
#world map
def create_world():
    world_map = [] 
    seed = random.randint(0, 100)
    for x in range(MAP_WIDTH): 
        column = [] 
        for y in range(MAP_HEIGHT):
            # World generation
            noise_value = pnoise2(x / SCALE, y / SCALE, octaves=8, persistence=0.5, lacunarity=4, repeatx=MAP_WIDTH, repeaty=MAP_HEIGHT, base=seed)
            # Normalize 0-1 for convinient transformation 
            normalized_value = (noise_value + 1) / 2
            # Map normalization (values not higher than 5, otherwise crash)
            terrain_difficulty = int(normalized_value*10)-2
            if terrain_difficulty < 1:#fixing small values
                terrain_difficulty = 1  
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
            #speed=30
            actor_pos[0] += dx / distance * speed
            actor_pos[1] += dy / distance * speed
            target=list(target)
            target[0] -= dx/distance * speed
            target[1] -= dy / distance * speed
            print(f"Actor pos: {actor_pos}, Speed: {speed}, Distance: {distance}")
    return target
