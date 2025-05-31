import mysql.connector  #надалі не забувай імпортовувати бібліотеки
import sys
import random
import pygame
import math
from logic import *

#Нагадую, все працює на костилях і через зад, не лізь лишній раз в код меню
def draw_text(screen, text, pos, font, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def main_menu(screen, clock, FPS):
    font = pygame.font.Font(None, 74)
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_text(screen, "Main Menu", (300, 100), font, (255, 255, 255))
        draw_text(screen, "New Game", (300, 200), font, (255, 255, 255))
        draw_text(screen, "Load Game", (300, 300), font, (255, 255, 255))
        draw_text(screen, "Achievements", (300, 400), font, (255, 255, 255))
        draw_text(screen, "Quit", (300, 500), font, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if 300 < mouse_pos[0] < 600 and 200 < mouse_pos[1] < 250:
                    return "new_game"
                if 300 < mouse_pos[0] < 600 and 300 < mouse_pos[1] < 350:
                    return "load_game"
                if 300 < mouse_pos[0] < 600 and 400 < mouse_pos[1] < 450:
                    achievements_menu(screen, clock, FPS, [])  #купи хліб з висівками
                if 300 < mouse_pos[0] < 600 and 500 < mouse_pos[1] < 550:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

def save_slot_menu(screen, clock, FPS, action):
    font = pygame.font.Font(None, 74)
    running = True
    while running:
        screen.fill((0, 0, 0))

        draw_text(screen, f"Select Slot to {action}", (100, 100), font, (255, 255, 255))
        draw_text(screen, "Slot 1", (100, 200), font, (255, 255, 255))
        draw_text(screen, "Slot 2", (100, 300), font, (255, 255, 255))
        draw_text(screen, "Slot 3", (100, 400), font, (255, 255, 255))
        draw_text(screen, "Back", (100, 500), font, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if 100 < mouse_pos[0] < 400 and 200 < mouse_pos[1] < 250:
                    return 1
                if 100 < mouse_pos[0] < 400 and 300 < mouse_pos[1] < 350:
                    return 2
                if 100 < mouse_pos[0] < 400 and 400 < mouse_pos[1] < 450:
                    return 3
                if 100 < mouse_pos[0] < 400 and 500 < mouse_pos[1] < 550:
                    return None

        pygame.display.flip()
        clock.tick(FPS)

def pause_menu(screen, clock, FPS, action_callback=None):
    font = pygame.font.Font(None, 74)
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_text(screen, "Pause Menu", (300, 100), font, (255, 255, 255))
        draw_text(screen, "Resume", (300, 200), font, (255, 255, 255))
        draw_text(screen, "Save Game", (300, 300), font, (255, 255, 255))
        draw_text(screen, "Load Game", (300, 400), font, (255, 255, 255))
        draw_text(screen, "Achievements", (300, 500), font, (255, 255, 255))
        draw_text(screen, "Quit", (300, 600), font, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if 300 < mouse_pos[0] < 600 and 200 < mouse_pos[1] < 250:  
                    return
                if 300 < mouse_pos[0] < 600 and 300 < mouse_pos[1] < 350:  
                    if action_callback:
                        slot = save_slot_menu(screen, clock, FPS, "Save")  
                        if slot:
                            action_callback("save_game", slot)  
                    return
                if 300 < mouse_pos[0] < 600 and 400 < mouse_pos[1] < 450:  
                    if action_callback:
                        action_callback("load_game")
                    return
                if 300 < mouse_pos[0] < 600 and 500 < mouse_pos[1] < 550:
                    achievements_menu(screen, clock, FPS, [])  #Підзагрузка ачівок(не забувай специфічну структуру)
                if 300 < mouse_pos[0] < 600 and 600 < mouse_pos[1] < 650:  #вихід(чомусь працює 50/50. Фіксити через мій труп)
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

#наступний код має бути в логіці, але я оголошую протест здоровому глузду
def achievements_menu(screen, clock, FPS, achievements):
    font = pygame.font.Font(None, 36)
    running = True

    #завантаження ачівок з БД
    unlocked_achievements = load_achievements_from_db()
    all_achievements = list(set(unlocked_achievements + achievements)) 

    while running:
        screen.fill((0, 0, 0)) 
        draw_text(screen, "Achievements", (300, 50), font, (255, 255, 255))

        if all_achievements:
            #показ ачівок(виявляється :D це теж треба прописувати щоб воно працювало)
            for i, achievement in enumerate(all_achievements):
                draw_text(screen, achievement, (50, 100 + i * 40), font, (255, 0, 0))
        else:
            draw_text(screen, "No achievements yet.", (300, 200), font, (255, 255, 255))

        draw_text(screen, "Press ESC to return", (300, 500), font, (255, 255, 255))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

def finished_game_menu(screen, clock, FPS, score):
    font = pygame.font.Font(None, 74)
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_text(screen, "Game Over", (300, 100), font, (255, 255, 255))
        draw_text(screen, f"Score: {score}", (300, 200), font, (255, 255, 255))
        draw_text(screen, "Main Menu", (300, 300), font, (255, 255, 255))
        draw_text(screen, "Quit", (300, 400), font, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if 300 < mouse_pos[0] < 600 and 300 < mouse_pos[1] < 350:  
                    return "main_menu"
                if 300 < mouse_pos[0] < 600 and 400 < mouse_pos[1] < 450:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)


    while running:
        screen.fill((0, 0, 0))
        draw_text(screen, "Login", (300, 100), font, (255, 255, 255))
        draw_text(screen, "Username:", (100, 200), input_font, (255, 255, 255))
        draw_text(screen, username, (300, 200), input_font, (255, 255, 255))
        draw_text(screen, "Password:", (100, 300), input_font, (255, 255, 255))
        draw_text(screen, "*" * len(password), (300, 300), input_font, (255, 255, 255))
        draw_text(screen, "Press ENTER to Login", (200, 400), input_font, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  #ENTER ЛОГІН 
                    if validate_login(username, password):
                        print("Login successful!")
                        return True
                    else:
                        print("Invalid username or password.")
                        username = ""
                        password = ""
                elif event.key == pygame.K_TAB:  #Роблю управління на кнопках
                    active_input = "password" if active_input == "username" else "username"
                elif event.key == pygame.K_BACKSPACE:  # щоб було видно що я вмію так
                    if active_input == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else: 
                    if active_input == "username":
                        username += event.unicode
                    else:
                        password += event.unicode

        pygame.display.flip()
        clock.tick(FPS)



def exploration_window(location_name):
    pygame.init()
    screen_width, screen_height = 800, 600
    exploration_screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"Exploring: {location_name}")

    # Ensure the location_name exists in LOCATION_PROPERTIES
    if location_name not in LOCATION_PROPERTIES:
        print(f"Error: Unknown location type '{location_name}'.")
        return

    # Retrieve location properties
    location_props = LOCATION_PROPERTIES[location_name]
    map_width, map_height = 50, 50  # Default map size
    num_rooms = location_props["num_rooms"]
    max_room_size = location_props["max_room_size"]
    min_room_size = location_props["min_room_size"]

    # Generate a random map using location properties
    game_map, rooms = generate_random_map(map_width, map_height, location_name)

    tile_size = 64  # Size of each map tile

    # Player properties
    fov = math.pi / 3  # Field of view (60 degrees)
    num_rays = 120  # Number of rays to cast
    max_depth = 2000  # Increased render distance
    ray_step = fov / num_rays  # Angle between each ray

    # Player properties
    player_x, player_y = rooms[0][0] * tile_size + tile_size // 2, rooms[0][1] * tile_size + tile_size // 2  # Start in the first room
    player_angle = 0  # Player's viewing angle
    player_speed = 3  # Movement speed
    player_hp = 100  # Player health
    player_shield = 50  # Player shield
    inventory = []  # Player inventory
    collected_pickups = set()  # Track collected pick-ups

    # Pick-Up Properties
    pick_ups = []

    def spawn_pickups():
        """Spawn pick-ups based on the location type."""
        pick_up_types = [
            ("weapon", 3),  # 3 weapon pick-ups
            ("ammo", 5),  # 5 ammo pick-ups
            ("heal", 3),  # 3 health pick-ups
            ("shield_upgrade", 2),  # 2 shield upgrades
            ("speed_upgrade", 2),  # 2 speed upgrades
            ("artifact", 1)  # 1 artifact
        ]

        for pick_up_type, count in pick_up_types:
            for _ in range(count):
                while True:
                    x = random.randint(1, map_width - 2)
                    y = random.randint(1, map_height - 2)
                    if game_map[y][x] == 0:  # Ensure the pick-up spawns on a floor tile
                        pick_ups.append({
                            "type": pick_up_type,
                            "x": x * tile_size + tile_size // 2,
                            "y": y * tile_size + tile_size // 2,
                            "collected": False
                        })
                        break

    spawn_pickups()

    def collect_pickups():
        """Check if the player is close to any pick-ups and collect them."""
        nonlocal player_hp, player_shield, player_speed, inventory
        for pick_up in pick_ups:
            if not pick_up["collected"]:
                distance = math.sqrt((player_x - pick_up["x"]) ** 2 + (player_y - pick_up["y"]) ** 2)
                if distance < tile_size:  # Player is close enough to collect the pick-up
                    pick_up["collected"] = True
                    collected_pickups.add(pick_up["type"])
                    if pick_up["type"] == "weapon":
                        inventory.append("weapon")
                        print("Picked up a weapon!")
                    elif pick_up["type"] == "ammo":
                        inventory.append("ammo")
                        print("Picked up ammo!")
                    elif pick_up["type"] == "heal":
                        player_hp = min(player_hp + 25, 100)
                        print("Picked up a health pack!")
                    elif pick_up["type"] == "shield_upgrade":
                        player_shield = min(player_shield + 25, 100)
                        print("Picked up a shield upgrade!")
                    elif pick_up["type"] == "speed_upgrade":
                        player_speed += 0.5
                        print("Picked up a speed upgrade!")
                    elif pick_up["type"] == "artifact":
                        inventory.append("artifact")
                        print("Picked up an artifact!")

    running = True
    clock = pygame.time.Clock()

    while running:
        exploration_screen.fill((0, 0, 0))  # Clear the screen

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Exit exploration screen
                    running = False

        # Handle movement
        keys = pygame.key.get_pressed()
        new_x, new_y = player_x, player_y

        if keys[pygame.K_w]:  # Move forward
            new_x += math.cos(player_angle) * player_speed
            new_y += math.sin(player_angle) * player_speed
        if keys[pygame.K_s]:  # Move backward
            new_x -= math.cos(player_angle) * player_speed
            new_y -= math.sin(player_angle) * player_speed
        if keys[pygame.K_a]:  # Strafe left
            new_x += math.cos(player_angle - math.pi / 2) * player_speed
            new_y += math.sin(player_angle - math.pi / 2) * player_speed
        if keys[pygame.K_d]:  # Strafe right
            new_x += math.cos(player_angle + math.pi / 2) * player_speed
            new_y += math.sin(player_angle + math.pi / 2) * player_speed

        # Check for collisions before updating position
        if game_map[int(new_y / tile_size)][int(new_x / tile_size)] == 0:
            player_x, player_y = new_x, new_y

        # Collect pick-ups
        collect_pickups()

        # Render the map
        for y in range(map_height):
            for x in range(map_width):
                color = (200, 200, 200) if game_map[y][x] == 1 else (50, 50, 50)
                pygame.draw.rect(exploration_screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))

        # Render pick-ups
        for pick_up in pick_ups:
            if not pick_up["collected"]:
                color = (0, 255, 0) if pick_up["type"] == "heal" else (255, 255, 0) if pick_up["type"] == "ammo" else (0, 0, 255)
                pygame.draw.circle(exploration_screen, color, (int(pick_up["x"]), int(pick_up["y"])), 5)

        # Render the player
        pygame.draw.circle(exploration_screen, (255, 0, 0), (int(player_x), int(player_y)), 10)

        # Render HUD
        font = pygame.font.Font(None, 36)
        hp_text = font.render(f"HP: {int(player_hp)}", True, (255, 0, 0))
        shield_text = font.render(f"Shield: {int(player_shield)}", True, (0, 255, 255))
        speed_text = font.render(f"Speed: {player_speed:.1f}", True, (255, 255, 0))
        inventory_text = font.render(f"Inventory: {', '.join(inventory)}", True, (255, 255, 255))
        exploration_screen.blit(hp_text, (10, 10))
        exploration_screen.blit(shield_text, (10, 40))
        exploration_screen.blit(speed_text, (10, 70))
        exploration_screen.blit(inventory_text, (10, 100))

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    # Restore the main game display
    pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TEIWAZ v_0.1")
