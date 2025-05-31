#Серце проекту
import pygame
import sys
from menu import *
from logic import *
pygame.init()

#параметри екрану
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("TEIWAZ v_0.1")

#фреймрейт
clock = pygame.time.Clock()
FPS = 24

#чек БД
setup_database()

#основний цикл
def main_loop(load_saved=False, save_name=None):
    if load_saved:
        # вибір сейв слоту(спочатку забув прописати і потім годину думав чому воно не працює)
        save_name = save_slot_menu(screen, clock, FPS, "Load")
        if save_name:
            seed, actor_pos, game_timer, inventory, objects, player_stats = load_game_from_db(save_name)
            if seed is None:
                print("No saved game found. Starting a new game.")
                world, seed = create_world()
                actor_pos = [0, 0]
                game_timer = 0
                inventory = []
                objects = []
                player_stats = {
                    "hp": 100,
                    "shield": 50,
                    "ammo": 10,
                    "railgun_bolts": 5,
                    "shotgun_shells": 8,
                    "current_weapon": "gun"
                }
            else:
                world, seed = create_world(seed)
        else:
            print("No save slot selected. Starting a new game.")
            world, seed = create_world()
            actor_pos = [0, 0]
            game_timer = 0
            inventory = []
            objects = []
            player_stats = {
                "hp": 100,
                "shield": 50,
                "ammo": 10,
                "railgun_bolts": 5,
                "shotgun_shells": 8,
                "current_weapon": "gun"
            }
    else:
        world, seed = create_world()
        actor_pos = [0, 0]
        game_timer = 0
        inventory = []  #ліст інвентаря(для того щоб легше вивантажити в БД)
        generate_structures(seed)  
        objects = load_objects_from_db(seed) 
        player_stats = {
            "hp": 100,
            "shield": 50,
            "ammo": 10,
            "railgun_bolts": 5,
            "shotgun_shells": 8,
            "current_weapon": "gun"
        }

    actor = pygame.image.load("assets/actor.png")
    actor_rect = actor.get_rect()
    target = [400, 300]
    inventory = [] 

    def handle_pause_action(action, slot=None):
        nonlocal seed, actor_pos, world, game_timer, inventory, objects

        if action == "save_game":
            if slot:
                save_game_to_db(slot, seed, actor_pos, game_timer, inventory, objects)
                print(f"Game saved to {slot}.")
        elif action == "load_game":
            save_name = save_slot_menu(screen, clock, FPS, "Load")
            if save_name:
                seed, actor_pos, game_timer, inventory, objects = load_game_from_db(save_name)
                if seed:
                    world, seed = create_world(seed)
                    print(f"Game loaded from {save_name}.")

    running = True
    needs_update = True  

    #таймер для ачівки "спідранер"
    font = pygame.font.Font(None, 36)

    while running:
        #бере реальний час а не відштовхується від кадрів що до біса круто
        game_timer += clock.get_time() / 1000 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                target = event.pos
                needs_update = True  
            if event.type == pygame.KEYDOWN:
                needs_update = True  #Гра іде на паузу коли гравець нічого не робить
                if event.key == pygame.K_F5:  #тому ми обновлюємо кадри при натиску кнопки
                    slot = save_slot_menu(screen, clock, FPS, "Save")
                    if slot:
                        save_game_to_db(slot, seed, actor_pos, game_timer, inventory)  #зберегти інвентар зразу прий ого оновленні
                if event.key == pygame.K_ESCAPE:  
                    pause_menu(screen, clock, FPS, handle_pause_action)
                if event.key == pygame.K_e:  #взаємодія з об'єктами
                    closest_obj = None#пуста змінна для сканера
                    min_distance = float('inf')

                    #сканер(працює основуючись на бд)
                    for obj in objects:
                        distance_to_obj = ((actor_pos[0] + 400 - obj["x"]) ** 2 + (actor_pos[1] + 300 - obj["y"]) ** 2) ** 0.5
                        if distance_to_obj < min_distance:
                            min_distance = distance_to_obj
                            closest_obj = obj
                    if closest_obj and min_distance < TILE_SIZE:
                        if closest_obj["discovered"]:
                            print(f"You have already explored the {closest_obj['type']} at ({closest_obj['x']}, {closest_obj['y']}).")
                        else:
                            if closest_obj["type"] != "extraction_point":
                                interaction_result = f"You looted a {closest_obj['type']}!"
                                inventory.append(closest_obj["type"])
                                closest_obj["discovered"] = True  # Позначаємо об'єкт як досліджений
                                mark_object_as_discovered(closest_obj["id"])  # Оновлюємо стан у базі даних
                                print(interaction_result)
                                print(f"Entering location: {closest_obj['type']}")
                                print(f"Player stats before entering: {player_stats}")
                                print(f"Inventory before entering: {inventory}")
                                inventory, player_stats = exploration_window(closest_obj["type"], inventory, player_stats)
                                print(f"Player stats after exiting: {player_stats}")
                                print(f"Inventory after exiting: {inventory}")
                            else:
                                print("You reached the extraction point!")
                                # Кінець гри
                                end_game(inventory, game_timer)
                            target = None
                    else:
                        print("No objects nearby to interact with.")

        if actor_pos != target:
            needs_update = True 

        #не знаю навіщо але я добавив оптимізацію... 
        if needs_update or actor_pos != target:  #коли ми рухаємося то оновлення екрану триває
            target = move_actor(actor_pos, target, world)
            camera_x = actor_pos[0]
            camera_y = actor_pos[1]

            screen.fill((0, 0, 0))
            render_world(screen, world, camera_x, camera_y, objects)
            screen.blit(actor, (screen.get_width() // 2 - actor_rect.width // 2, screen.get_height() // 2 - actor_rect.height // 2))
            
            #тут далі перелік всіх таймерів і показників
            #рендер таймеру
            timer_text = font.render(f"Time: {int(game_timer)}s", True, (0, 255, 0)) 
            screen.blit(timer_text, (10, 10)) 

            # корди
            player_coords_text = font.render(f"Player: ({int(actor_pos[0]+400)}, {int(actor_pos[1]+300)})", True, (255, 255, 255))
            screen.blit(player_coords_text, (10, 50))

            # найближчий не відкритий об'єкт
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
                screen.blit(closest_obj_text, (10, 80))  

            extraction_coords = next((obj for obj in objects if obj["type"] == "extraction_point"), None)
            if extraction_coords:
                extraction_coords_text = font.render(f"Extraction: ({extraction_coords['x']}, {extraction_coords['y']})", True, (255, 255, 255))
                screen.blit(extraction_coords_text, (10, 110))

            if target:
                pygame.draw.circle(screen, (0, 255, 0), (target[0], target[1]), 5)
            pygame.display.flip()
            needs_update = False  #вимикає необхідність оновлення екрану після його оновлення(вау)

        #Динамічний фреймрейт
        if needs_update or actor_pos != target:  #На даний момент ця частину коду не виконує ніякої роботи
            clock.tick(FPS) #але я її не чіпаю, бо в майбутньому планую замінити нинішню систему на неї
        else:
            clock.tick(1)  #але ж цікавий концепт? чи не так?

    pygame.quit()
    sys.exit()

def end_game(inventory, game_timer):
    score = len(inventory) * 100  #100 гривень за кожен предмет
    print(f"Game Over! Your score: {score}")
    print(f"Time: {int(game_timer)} seconds")
    print(f"Inventory: {', '.join(inventory) if inventory else 'Empty'}")

    achievements = check_achievements(score, game_timer, inventory)

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