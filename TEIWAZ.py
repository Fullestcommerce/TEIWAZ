#Серце проекту
import pygame
import sys
from menu import *
from logic import *
pygame.init()
    #параметри екрану
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("TEIWAZ v_0.1")
    #фреймрейт(поки визначає тільки швидкість оновлення кадрів при динамічному рухові)
clock = pygame.time.Clock()
FPS=24

#чек БД
setup_database()

    #основний цикл
def main_loop(load_saved=False, save_name=None):
    if load_saved:
        # Menu for selecting a save slot
        save_name = save_slot_menu(screen, clock, FPS, "Load")
        if save_name:
            seed, actor_pos, game_timer, inventory = load_game_from_db(save_name)
            if seed is None:
                print("No saved game found. Starting a new game.")
                world, seed = create_world()
                actor_pos = [0, 0]
                game_timer = 0
                inventory = []  # Initialize inventory
            else:
                world, seed = create_world(seed)
                generate_structures(seed)  # Generate structures for the seed
                objects = load_objects_from_db(seed)  # Load objects for the seed
        else:
            print("No save slot selected. Starting a new game.")
            world, seed = create_world()
            actor_pos = [0, 0]
            game_timer = 0
            inventory = []  # Initialize inventory
    else:
        world, seed = create_world()
        actor_pos = [0, 0]
        game_timer = 0
        inventory = []  # Initialize inventory
        generate_structures(seed)  # Generate structures for the seed
        objects = load_objects_from_db(seed)  # Load objects for the seed

    actor = pygame.image.load("assets/actor.png")
    actor_rect = actor.get_rect()
    target = [400, 300]
    inventory = []  # Initialize inventory

    def handle_pause_action(action, slot=None):
        nonlocal seed, actor_pos, world, game_timer, inventory  # Declare nonlocal variables at the start

        if action == "save_game":
            if slot:
                save_game_to_db(slot, seed, actor_pos, game_timer, inventory)
                print(f"Game saved to {slot}.")
        elif action == "load_game":
            save_name = save_slot_menu(screen, clock, FPS, "Load")
            if save_name:
                seed, actor_pos, game_timer, inventory = load_game_from_db(save_name)
                if seed:
                    world, seed = create_world(seed)
                    print(f"Game loaded from {save_name}.")

    running = True
    needs_update = True  

    # Initialize timer
    font = pygame.font.Font(None, 36)  # Font for displaying the timer

    while running:
        # Increment the timer based on the frame rate
        game_timer += clock.get_time() / 1000  # Convert milliseconds to seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                target = event.pos
                needs_update = True  
            if event.type == pygame.KEYDOWN:
                needs_update = True  # Updates the game when a key is pressed
                if event.key == pygame.K_F5:  # Save the game when F5 is pressed
                    slot = save_slot_menu(screen, clock, FPS, "Save")
                    if slot:
                        save_game_to_db(slot, seed, actor_pos, game_timer, inventory)  # Pass inventory to save function
                if event.key == pygame.K_ESCAPE:  # Pause the game
                    pause_menu(screen, clock, FPS, handle_pause_action)
                if event.key == pygame.K_e:  # Interact with objects
                    closest_obj = None
                    min_distance = float('inf')

                    # Object scanner
                    for obj in objects:
                        distance_to_obj = ((actor_pos[0] + 400 - obj["x"]) ** 2 + (actor_pos[1] + 300 - obj["y"]) ** 2) ** 0.5
                        if distance_to_obj < min_distance:
                            min_distance = distance_to_obj
                            closest_obj = obj
                    if closest_obj and min_distance < TILE_SIZE:
                        if closest_obj["type"] != "extraction_point":
                            interaction_result = f"You salvaged a {closest_obj['type']}!"
                            inventory.append(closest_obj["type"])  # Add to inventory
                            closest_obj["discovered"] = True  # Mark as discovered
                            print(interaction_result)
                        else:
                            print("You reached the extraction point!")
                            # End the game
                            end_game(inventory, game_timer)
                        target = None  # Stop movement after interaction
                    else:
                        print("No objects nearby to interact with.")

        if actor_pos != target:
            needs_update = True 

        # Optimization: Only update the screen when needed
        if needs_update or actor_pos != target:  # Keep updating while the actor is moving
            target = move_actor(actor_pos, target, world)
            camera_x = actor_pos[0]
            camera_y = actor_pos[1]

            screen.fill((0, 0, 0))
            render_world(screen, world, camera_x, camera_y, objects)
            screen.blit(actor, (screen.get_width() // 2 - actor_rect.width // 2, screen.get_height() // 2 - actor_rect.height // 2))
            
            # Display the timer in the top-left corner
            timer_text = font.render(f"Time: {int(game_timer)}s", True, (0, 255, 0))  # Green color
            screen.blit(timer_text, (10, 10))  # Top-left corner

            # Display coordinates
            player_coords_text = font.render(f"Player: ({int(actor_pos[0]+400)}, {int(actor_pos[1]+300)})", True, (255, 255, 255))
            screen.blit(player_coords_text, (10, 50))  # Below the timer

            # Display closest not-looted object
            closest_obj = None
            min_distance = float('inf')
            for obj in objects:
                if not obj["discovered"]:
                    distance = ((actor_pos[0] - obj["x"]) ** 2 + (actor_pos[1] - obj["y"]) ** 2) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        closest_obj = obj

            if closest_obj:
                closest_obj_text = font.render(f"Closest: {closest_obj['type']} at ({closest_obj['x']}, {closest_obj['y']})", True, (255, 255, 255))
                screen.blit(closest_obj_text, (10, 80))  # Below player coordinates

            extraction_coords = next((obj for obj in objects if obj["type"] == "extraction_point"), None)
            if extraction_coords:
                extraction_coords_text = font.render(f"Extraction: ({extraction_coords['x']}, {extraction_coords['y']})", True, (255, 255, 255))
                screen.blit(extraction_coords_text, (10, 110))  # Below player coordinates

            if target:
                pygame.draw.circle(screen, (0, 255, 0), (target[0], target[1]), 5)
            pygame.display.flip()
            needs_update = False  # Reset the flag after updating

        # Adjust FPS dynamically
        if needs_update or actor_pos != target:  # Use full FPS while updates or movement are active
            clock.tick(FPS)
        else:
            clock.tick(1)  # Use a very low FPS when idle

    pygame.quit()
    sys.exit()

def end_game(inventory, game_timer):
    score = len(inventory) * 100  # Each item is worth 100 points
    print(f"Game Over! Your score: {score}")
    print(f"Time: {int(game_timer)} seconds")
    print(f"Inventory: {', '.join(inventory) if inventory else 'Empty'}")

    # Check achievements
    achievements = check_achievements(score, game_timer, inventory)

    # Display achievements menu
    achievements_menu(screen, clock, FPS, achievements)

    pygame.quit()
    sys.exit()

#гарно гарно
if __name__ == "__main__":
    act = main_menu(screen, clock, FPS)
    if act == "new_game":
        main_loop(load_saved=False)
    elif act:
        main_loop(load_saved=True, save_name=act)
    pygame.quit()
    sys.exit()