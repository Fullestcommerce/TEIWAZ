import pygame
import mysql.connector  # Add this import for database operations
import sys
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
                    achievements_menu(screen, clock, FPS, [])  # Pass an empty list for achievements
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
                if 300 < mouse_pos[0] < 600 and 200 < mouse_pos[1] < 250:  # Resume
                    return
                if 300 < mouse_pos[0] < 600 and 300 < mouse_pos[1] < 350:  # Save Game
                    if action_callback:
                        slot = save_slot_menu(screen, clock, FPS, "Save")  # Call save_slot_menu
                        if slot:
                            action_callback("save_game", slot)  # Pass the slot to the callback
                    return
                if 300 < mouse_pos[0] < 600 and 400 < mouse_pos[1] < 450:  # Load Game
                    if action_callback:
                        action_callback("load_game")
                    return
                if 300 < mouse_pos[0] < 600 and 500 < mouse_pos[1] < 550:  # Achievements
                    achievements_menu(screen, clock, FPS)
                if 300 < mouse_pos[0] < 600 and 600 < mouse_pos[1] < 650:  # Quit
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

def achievements_menu(screen, clock, FPS, achievements):
    font = pygame.font.Font(None, 36)
    running = True

    # Load previously unlocked achievements from the database
    unlocked_achievements = load_achievements_from_db()
    all_achievements = list(set(unlocked_achievements + achievements))  # Combine and deduplicate

    while running:
        screen.fill((0, 0, 0))  # Clear the screen
        draw_text(screen, "Achievements", (300, 50), font, (255, 255, 255))

        if all_achievements:
            # Display each achievement
            for i, achievement in enumerate(all_achievements):
                draw_text(screen, achievement, (50, 100 + i * 40), font, (255, 0, 0))  # Red text for achievements
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
                if 300 < mouse_pos[0] < 600 and 300 < mouse_pos[1] < 350:  # Main Menu
                    return "main_menu"
                if 300 < mouse_pos[0] < 600 and 400 < mouse_pos[1] < 450:  # Quit
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)