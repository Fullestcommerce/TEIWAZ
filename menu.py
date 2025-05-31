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

    # Generate a random map
    map_width, map_height = 50, 50
    num_rooms = 10
    max_room_size, min_room_size = 10, 5
    game_map, rooms = generate_random_map(map_width, map_height, location_name)

    tile_size = 64  # Size of each map tile
    fov = math.pi / 3  # Field of view (60 degrees)
    num_rays = 120  # Number of rays to cast
    max_depth = 2000  # Increased render distance
    ray_step = fov / num_rays  # Angle between each ray

    # Player properties
    player_x, player_y = rooms[0][0] * tile_size + tile_size // 2, rooms[0][1] * tile_size + tile_size // 2  # Start in the first room
    player_angle = 0  # Player's viewing angle
    player_speed = 3  # Movement speed
    rotation_speed = 0.05  # Rotation speed
    player_hp = 100  # Player health
    player_shield = 50  # Player shield
    shield_regen_rate = 0.1  # Shield regeneration per frame
    player_ammo = 10  # Ammo for Gun
    railgun_bolts = 5  # Ammo for Railgun
    shotgun_shells = 8  # Ammo for Shotgun
    shoot_cooldown = 0  # Cooldown timer for shooting
    current_weapon = "gun"  # Default weapon

    # Enemy properties
    enemies = []

    def spawn_enemies():
        """Spawn enemies based on the location type."""
        enemy_config = LOCATION_PROPERTIES[location_name]["enemies"]
        for enemy_type, count in enemy_config:
            for _ in range(count):
                while True:
                    x = random.randint(1, map_width - 2)
                    y = random.randint(1, map_height - 2)
                    if game_map[y][x] == 0:  # Ensure the enemy spawns on a floor tile
                        enemies.append({
                            "type": enemy_type,
                            "x": x * tile_size + tile_size // 2,
                            "y": y * tile_size + tile_size // 2,
                            "hp": 50 if enemy_type == "drone" else 100 if enemy_type == "robot" else 150,
                            "speed": 4 if enemy_type == "drone" else 2 if enemy_type == "robot" else 1,
                            "attack_range": 3 if enemy_type == "drone" else 5 if enemy_type == "robot" else 3,  # Increased drone attack range
                            "damage": 10 if enemy_type == "drone" else 20 if enemy_type == "robot" else 30,
                            "aggro_range": 10 * tile_size,  # Distance at which the enemy starts chasing the player
                            "min_distance": 2 * tile_size,  # Minimum distance to maintain from the player
                            "attack_cooldown": 0,  # Cooldown timer for enemy attacks
                        })
                        break

    spawn_enemies()

    running = True
    clock = pygame.time.Clock()

    def is_visible(x, y):
        """Check if a point (x, y) is visible to the player using raycasting."""
        dx = x - player_x
        dy = y - player_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        angle_to_point = math.atan2(dy, dx)
        angle_diff = (angle_to_point - player_angle + math.pi) % (2 * math.pi) - math.pi

        if -fov / 2 <= angle_diff <= fov / 2 and distance < max_depth:
            # Cast a ray to check for walls blocking the view
            sin_a = math.sin(angle_to_point)
            cos_a = math.cos(angle_to_point)
            for depth in range(1, int(distance)):
                target_x = int((player_x + cos_a * depth) / tile_size)
                target_y = int((player_y + sin_a * depth) / tile_size)
                if game_map[target_y][target_x] == 1:
                    return False  # Wall blocks the view
            return True
        return False

    def cast_rays():
        """Cast rays and render the 3D environment."""
        for ray in range(num_rays):
            ray_angle = player_angle - (fov / 2) + (ray * ray_step)
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            depth = 0
            hit = False
            while not hit and depth < max_depth:
                depth += 1
                target_x = int((player_x + cos_a * depth) / tile_size)
                target_y = int((player_y + sin_a * depth) / tile_size)

                if target_x < 0 or target_x >= len(game_map[0]) or target_y < 0 or target_y >= len(game_map):
                    break  # Out of bounds
                if game_map[target_y][target_x] == 1:
                    hit = True

            # Calculate wall height based on depth
            if hit:
                wall_height = int(screen_height / (depth * 0.01))
                color = (255 - min(depth, 255), 255 - min(depth, 255), 255 - min(depth, 255))  # Darken with distance
                pygame.draw.rect(exploration_screen, color, (ray * (screen_width // num_rays), (screen_height // 2) - (wall_height // 2), (screen_width // num_rays), wall_height))

        # Render enemies in the 3D view
        for enemy in enemies:
            dx = enemy["x"] - player_x
            dy = enemy["y"] - player_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Check if the enemy is visible
            if is_visible(enemy["x"], enemy["y"]):
                # Calculate enemy height and position
                angle_to_enemy = math.atan2(dy, dx)
                angle_diff = (angle_to_enemy - player_angle + math.pi) % (2 * math.pi) - math.pi
                enemy_height = int(screen_height / (distance * 0.01))
                enemy_screen_x = int((angle_diff + fov / 2) / fov * screen_width)
                color = (255, 0, 0) if enemy["type"] == "drone" else (255, 165, 0) if enemy["type"] == "robot" else (0, 0, 255)
                pygame.draw.rect(exploration_screen, color, (enemy_screen_x - 5, (screen_height // 2) - (enemy_height // 2), 10, enemy_height))

    def render_minimap():
                """Render a top-down minimap in the top-right corner."""
                minimap_scale = 4  # Scale factor for the minimap
                minimap_width = map_width * minimap_scale
                minimap_height = map_height * minimap_scale
                minimap_surface = pygame.Surface((minimap_width, minimap_height))
                minimap_surface.fill((50, 50, 50))  # Background color for the minimap

                # Draw the map
                for y in range(map_height):
                    for x in range(map_width):
                        color = (200, 200, 200) if game_map[y][x] == 1 else (0, 0, 0)
                        pygame.draw.rect(minimap_surface, color, (x * minimap_scale, y * minimap_scale, minimap_scale, minimap_scale))

                # Draw the player on the minimap
                player_minimap_x = int(player_x / tile_size * minimap_scale)
                player_minimap_y = int(player_y / tile_size * minimap_scale)
                pygame.draw.circle(minimap_surface, (0, 255, 0), (player_minimap_x, player_minimap_y), 3)

                # Draw enemies on the minimap
                for enemy in enemies:
                    enemy_minimap_x = int(enemy["x"] / tile_size * minimap_scale)
                    enemy_minimap_y = int(enemy["y"] / tile_size * minimap_scale)
                    color = (255, 0, 0) if enemy["type"] == "drone" else (255, 165, 0) if enemy["type"] == "robot" else (0, 0, 255)
                    pygame.draw.circle(minimap_surface, color, (enemy_minimap_x, enemy_minimap_y), 3)

                # Blit the minimap onto the main screen
                exploration_screen.blit(minimap_surface, (screen_width - minimap_width - 10, 10))

    def update_enemies():
        """Update enemy positions and behavior."""
        for enemy in enemies:
            dx = player_x - enemy["x"]
            dy = player_y - enemy["y"]
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < enemy["aggro_range"] and distance > enemy["min_distance"]:
                # Convert enemy and player positions to grid coordinates
                enemy_pos = (int(enemy["x"] / tile_size), int(enemy["y"] / tile_size))
                player_pos = (int(player_x / tile_size), int(player_y / tile_size))

                # Find path to the player using A* pathfinding
                path = a_star_search(game_map, enemy_pos, player_pos)

                if path:
                    # Move toward the next step in the path
                    next_step = path[0]
                    new_x = next_step[0] * tile_size + tile_size // 2
                    new_y = next_step[1] * tile_size + tile_size // 2

                    # Smooth movement
                    angle = math.atan2(new_y - enemy["y"], new_x - enemy["x"])
                    enemy["x"] += math.cos(angle) * enemy["speed"]
                    enemy["y"] += math.sin(angle) * enemy["speed"]

            # Enemy attacks the player
            if distance <= enemy["attack_range"] * tile_size and enemy["attack_cooldown"] <= 0:
                nonlocal player_hp, player_shield
                if player_shield > 0:
                    player_shield -= enemy["damage"]
                    if player_shield < 0:
                        player_hp += player_shield  # Apply leftover damage to health
                        player_shield = 0
                else:
                    player_hp -= enemy["damage"]
                enemy["attack_cooldown"] = 60  # Cooldown for enemy attacks

        # Decrease enemy attack cooldown
        for enemy in enemies:
            if enemy["attack_cooldown"] > 0:
                enemy["attack_cooldown"] -= 1

    def shoot():
        """Handle player shooting."""
        nonlocal player_ammo, railgun_bolts, shotgun_shells
        if current_weapon == "gun":
            if player_ammo > 0:
                player_ammo -= 1
                damage = 50
            else:
                print("Out of ammo!")
                return
        elif current_weapon == "railgun":
            if railgun_bolts > 0:
                railgun_bolts -= 1
                damage = 100
            else:
                print("Out of railgun bolts!")
                return
        elif current_weapon == "shotgun":
            if shotgun_shells > 0:
                shotgun_shells -= 1
                damage = 75
            else:
                print("Out of shotgun shells!")
                return
        elif current_weapon == "power_fist":
            damage = 30  # Power fist doesn't require ammo
        else:
            print("No weapon selected!")
            return

        # Apply damage to enemies in line of sight
        enemies_to_remove = []  # Track enemies to remove after the loop
        for enemy in enemies:
            dx = enemy["x"] - player_x
            dy = enemy["y"] - player_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Check if the enemy is in the player's line of sight
            if is_visible(enemy["x"], enemy["y"]) and distance < max_depth:
                enemy["hp"] -= damage
                if enemy["hp"] <= 0:
                    enemies_to_remove.append(enemy)
                    print(f"Enemy {enemy['type']} defeated!")

        # Remove defeated enemies after the loop to avoid modifying the list while iterating
        for enemy in enemies_to_remove:
            enemies.remove(enemy)

        # Set the cooldown for the next shot
        shoot_cooldown = 30  # Adjust cooldown as needed

    def update_shield():
        """Regenerate the player's shield."""
        nonlocal player_shield
        player_shield = min(player_shield + shield_regen_rate, 50)

    while running:
        exploration_screen.fill((0, 0, 0))  # Clear the screen

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Exit exploration screen
                    running = False
                if event.key == pygame.K_SPACE:  # Shoot
                    shoot()
                if event.key == pygame.K_1:
                    current_weapon = "gun"
                if event.key == pygame.K_2:
                    current_weapon = "railgun"
                if event.key == pygame.K_3:
                    current_weapon = "shotgun"
                if event.key == pygame.K_4:
                    current_weapon = "power_fist"

        # Handle movement with collision detection
        keys = pygame.key.get_pressed()
        new_x, new_y = player_x, player_y
        if keys[pygame.K_w]:  # Move forward
            new_x += math.cos(player_angle) * player_speed
            new_y += math.sin(player_angle) * player_speed
        if keys[pygame.K_s]:  # Move backward
            new_x -= math.cos(player_angle) * player_speed
            new_y -= math.sin(player_angle) * player_speed
        if keys[pygame.K_LEFT]:  # Strafe left
            new_x -= math.sin(player_angle) * player_speed
            new_y += math.cos(player_angle) * player_speed
        if keys[pygame.K_RIGHT]:  # Strafe right
            new_x += math.sin(player_angle) * player_speed
            new_y -= math.cos(player_angle) * player_speed

        # Check for collisions before updating position
        if game_map[int(new_y / tile_size)][int(new_x / tile_size)] == 0:
            player_x, player_y = new_x, new_y

        if keys[pygame.K_a]:  # Rotate left
            player_angle -= rotation_speed
        if keys[pygame.K_d]:  # Rotate right
            player_angle += rotation_speed

        # Update shield
        update_shield()

        # Update enemies
        update_enemies()

        # Cast rays and render the environment
        cast_rays()

        # Render the minimap
        render_minimap()

        # Render HUD
        font = pygame.font.Font(None, 36)
        hp_text = font.render(f"HP: {player_hp}", True, (255, 0, 0))
        shield_text = font.render(f"Shield: {int(player_shield)}", True, (0, 255, 255))
        ammo_text = font.render(f"Ammo: {player_ammo}", True, (255, 255, 0))
        railgun_text = font.render(f"Railgun Bolts: {railgun_bolts}", True, (255, 165, 0))
        shotgun_text = font.render(f"Shotgun Shells: {shotgun_shells}", True, (255, 165, 0))
        weapon_text = font.render(f"Weapon: {current_weapon.capitalize()}", True, (255, 255, 255))
        exploration_screen.blit(hp_text, (10, 10))
        exploration_screen.blit(shield_text, (10, 40))
        exploration_screen.blit(ammo_text, (10, 70))
        exploration_screen.blit(railgun_text, (10, 100))
        exploration_screen.blit(shotgun_text, (10, 130))
        exploration_screen.blit(weapon_text, (10, 160))

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    # Restore the main game display
    pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TEIWAZ v_0.1")
