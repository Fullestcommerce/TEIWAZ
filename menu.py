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

    # Map (1 = wall, 0 = empty space)
    game_map = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ]

    tile_size = 64  # Size of each map tile
    fov = math.pi / 3  # Field of view (60 degrees)
    num_rays = 120  # Number of rays to cast
    max_depth = 800  # Maximum depth of raycasting
    ray_step = fov / num_rays  # Angle between each ray

    # Player properties
    player_x, player_y = 150, 150  # Player's position
    player_angle = 0  # Player's viewing angle
    player_speed = 3  # Movement speed
    rotation_speed = 0.05  # Rotation speed

    running = True
    clock = pygame.time.Clock()

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
        if keys[pygame.K_w]:  # Move forward
            player_x += math.cos(player_angle) * player_speed
            player_y += math.sin(player_angle) * player_speed
        if keys[pygame.K_s]:  # Move backward
            player_x -= math.cos(player_angle) * player_speed
            player_y -= math.sin(player_angle) * player_speed
        if keys[pygame.K_a]:  # Rotate left
            player_angle -= rotation_speed
        if keys[pygame.K_d]:  # Rotate right
            player_angle += rotation_speed

        # Cast rays and render the environment
        cast_rays()

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    # Restore the main game display
    pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TEIWAZ v_0.1")
