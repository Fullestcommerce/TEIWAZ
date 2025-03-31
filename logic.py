import pygame
import random
from noise import pnoise2
import json
import mysql.connector

TILE_SIZE=32
MAP_WIDTH=300 
MAP_HEIGHT=300
SCALE=100
def setup_database():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111"
        )
        cursor = connection.cursor()

        # Check and create the database
        cursor.execute("CREATE DATABASE IF NOT EXISTS teiwaz_game")
        cursor.execute("USE teiwaz_game")

        # Create or update the saves table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saves (
                id INT NOT NULL PRIMARY KEY,  -- Use id as the primary key
                save_name VARCHAR(255) NOT NULL,
                seed INT NOT NULL,
                actor_pos_x FLOAT NOT NULL,
                actor_pos_y FLOAT NOT NULL,
                game_timer FLOAT NOT NULL,
                inventory TEXT DEFAULT NULL,
                progress TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create or update the objects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                object_type VARCHAR(255) NOT NULL,
                pos_x INT NOT NULL,
                pos_y INT NOT NULL,
                seed INT NOT NULL,
                discovered BOOLEAN DEFAULT FALSE
            )
        """)

        # Create or update the achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,  -- Achievement name must be unique
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of when the achievement was unlocked
            );
        """)

        # Insert default achievements if they don't exist
        default_achievements = [
            ("High Score", "Reach a score higher than 1000", False),
            ("Speed Runner", "Finish the game in under 180 seconds", False),
            ("Minimalist", "Finish the game with an empty inventory", False)
        ]
        for name, description, unlocked in default_achievements:
            cursor.execute("""
                INSERT IGNORE INTO achievements (name, description, unlocked)
                VALUES (%s, %s, %s)
            """, (name, description, unlocked))

        connection.commit()
        print("Database setup completed successfully.")
    except mysql.connector.Error as err:
        print(f"Error setting up the database: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

#Генератор світу
def create_world(seed=None):
    if seed is None:
        seed = random.randint(0, 100)
    world_map = []
    for x in range(MAP_WIDTH):
        column = []
        for y in range(MAP_HEIGHT):
            #Алгоритм шуму перліна на основі сіду
            noise_value = pnoise2(x / SCALE, y / SCALE, octaves=8, persistence=0.5, lacunarity=4, repeatx=MAP_WIDTH, repeaty=MAP_HEIGHT, base=seed)
            #Нормалізація шуму в зручні для перетворення значення 
            normalized_value = (noise_value + 1) / 2
            #Нормалізація для генерації карти висот(дуже чутлива формула, не лізь лишній раз)
            terrain_difficulty = int(normalized_value*10)-2
            if terrain_difficulty < 1:#мінімальна висота(уникає крашів)
                terrain_difficulty = 1  
            column.append(terrain_difficulty)
        world_map.append(column)
    return world_map, seed

def render_world(screen, world_map, camera_x, camera_y, objects):
    #рендер висот
    for x in range(MAP_WIDTH): 
        for y in range(MAP_HEIGHT): 
            tile_color = (world_map[x][y] * 50, world_map[x][y] * 50, world_map[x][y] * 50) 
            pygame.draw.rect(screen, tile_color, (x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE))
    
    #рендер об'єктів за типом(витяжка з бд)
    for obj in objects:
        obj_image = pygame.image.load(f"assets/{obj['type']}.png")  # Load object image
        screen.blit(obj_image, (obj["x"] - camera_x, obj["y"] - camera_y))  # Draw object at its position

def move_actor(actor_pos, target, world_map):
    if target:
        dx = target[0]-400
        dy = target[1]-300
        print(dx, dy)
        distance = (dx**2 + dy**2) ** 0.5
        if distance < 5:
            target = None
        else:
            x, y = (actor_pos[0]+400)/TILE_SIZE, (actor_pos[1]+300)/TILE_SIZE
            print(f"X: {x}, Y: {y}")
            speed=min(5/world_map[int(x)][int(y)],5)
            #speed=30
            actor_pos[0] += dx / distance * speed
            actor_pos[1] += dy / distance * speed
            target=list(target)
            target[0] -= dx/distance * speed
            target[1] -= dy / distance * speed
            print(f"Actor pos: {actor_pos}, Speed: {speed}, Distance: {distance}")
    return target



def save_game_to_db(save_id, seed, actor_pos, game_timer, inventory):
    connection = None
    try:
        # Ensure save_id is an integer
        if isinstance(save_id, str) and save_id.startswith("Slot "):
            save_id = int(save_id.split(" ")[1])  # Extract the numeric part of "Slot X"

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()

        inventory_str = ",".join(inventory)  # Convert inventory to a string

        query = """
            INSERT INTO saves (id, save_name, seed, actor_pos_x, actor_pos_y, game_timer, inventory)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            save_name = VALUES(save_name),
            seed = VALUES(seed),
            actor_pos_x = VALUES(actor_pos_x),
            actor_pos_y = VALUES(actor_pos_y),
            game_timer = VALUES(game_timer),
            inventory = VALUES(inventory)
        """
        save_name = f"Slot {save_id}"  # Generate a save name based on the id

        # Debugging: Print the values being inserted
        print(f"Saving game to database with values:")
        print(f"ID: {save_id}, Save Name: {save_name}, Seed: {seed}, Actor Pos: {actor_pos}, Game Timer: {game_timer}, Inventory: {inventory_str}")

        cursor.execute(query, (save_id, save_name, seed, actor_pos[0], actor_pos[1], game_timer, inventory_str))
        connection.commit()
        print(f"Game saved successfully to slot ID: {save_id}")
    except mysql.connector.Error as err:
        print(f"Error saving game: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def load_game_from_db(save_id):
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()

        query = """
            SELECT seed, actor_pos_x, actor_pos_y, game_timer, inventory
            FROM saves
            WHERE id = %s
        """
        print(f"Loading from slot ID: {save_id}")
        cursor.execute(query, (save_id,))
        result = cursor.fetchone()
        if (result):
            seed, actor_pos_x, actor_pos_y, game_timer, inventory_str = result
            inventory = inventory_str.split(",") if inventory_str else []  # Convert inventory string back to a list
            print(f"Data loaded: seed={seed}, actor_pos={[actor_pos_x, actor_pos_y]}, game_timer={game_timer}, inventory={inventory}")
            return seed, [actor_pos_x, actor_pos_y], game_timer, inventory
        else:
            print(f"No save found for slot ID: {save_id}")
            # Return default values if no save is found
            return None, [0, 0], 0, []
    except mysql.connector.Error as err:
        print(f"Error loading game: {err}")
        return None, [0, 0], 0, []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def list_saves():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()
        query = "SELECT save_name FROM saves"
        cursor.execute(query)
        saves = cursor.fetchall()
        return [save[0] for save in saves]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_object_to_db(object_type, pos_x, pos_y):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()

        query = """
            INSERT INTO objects (object_type, pos_x, pos_y)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (object_type, pos_x, pos_y))
        connection.commit()
        print(f"Object '{object_type}' saved at ({pos_x}, {pos_y}).")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def load_objects_from_db(seed):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()

        query = "SELECT object_type, pos_x, pos_y, discovered FROM objects WHERE seed = %s"
        cursor.execute(query, (seed,))
        objects = cursor.fetchall()
        return [{"type": obj[0], "x": obj[1], "y": obj[2], "discovered": obj[3]} for obj in objects]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_structures(seed):
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()

        # Clean the objects table for the given seed
        cursor.execute("DELETE FROM objects WHERE seed = %s", (seed,))

        # Default structures
        structures = [
            {"type": "crash_site", "x": 320, "y": 320}
        ]

        # Generate random structures
        random.seed(seed)
        num_ruins = random.randint(10, 16)
        num_charging_stations = random.randint(4, 6)
        num_fuel_depots = random.randint(4, 6)
        num_salvaged_parts = random.randint(8, 12)
        num_extraction_points = 1

        # Helper function to generate random positions
        def random_position():
            return random.randint(0, MAP_WIDTH * TILE_SIZE), random.randint(0, MAP_HEIGHT * TILE_SIZE)

        # Add ruins
        for _ in range(num_ruins):
            x, y = random_position()
            structures.append({"type": "ruins", "x": x, "y": y})

        # Add charging stations
        for _ in range(num_charging_stations):
            x, y = random_position()
            structures.append({"type": "charging_station", "x": x, "y": y})

        # Add fuel depots
        for _ in range(num_fuel_depots):
            x, y = random_position()
            structures.append({"type": "fuel_depot", "x": x, "y": y})

        # Add salvaged parts
        for _ in range(num_salvaged_parts):
            x, y = random_position()
            structures.append({"type": "salvaged_parts", "x": x, "y": y})

        # Add extraction point
        for _ in range(num_extraction_points):
            x, y = random_position()
            structures.append({"type": "extraction_point", "x": x, "y": y})

        # Insert structures into the database
        for structure in structures:
            cursor.execute("""
                INSERT INTO objects (object_type, pos_x, pos_y, seed, discovered)
                VALUES (%s, %s, %s, %s, %s)
            """, (structure["type"], structure["x"], structure["y"], seed, False))

        connection.commit()
        print(f"Generated {len(structures)} structures for seed {seed}.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def check_achievements(score, game_timer, inventory):
    achievements = []

    # Add achievements based on conditions
    if score > 1000:
        achievement = "High Score: Reach a score higher than 1000"
        achievements.append(achievement)
        save_achievement_to_db(achievement)  # Save to database

    if game_timer < 180:
        achievement = "Speed Runner: Finish the game in under 180 seconds"
        achievements.append(achievement)
        save_achievement_to_db(achievement)  # Save to database

    if not inventory:
        achievement = "Minimalist: Finish the game with an empty inventory"
        achievements.append(achievement)
        save_achievement_to_db(achievement)  # Save to database

    # Return unique achievements
    return list(set(achievements))  # Remove duplicates

def save_achievement_to_db(achievement_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()

        query = """
            INSERT INTO achievements (name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE
            unlocked_at = CURRENT_TIMESTAMP
        """
        cursor.execute(query, (achievement_name,))
        connection.commit()
        print(f"Achievement saved: {achievement_name}")
    except mysql.connector.Error as err:
        print(f"Error saving achievement: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def load_achievements_from_db():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        cursor = connection.cursor()

        query = "SELECT name FROM achievements"
        cursor.execute(query)
        results = cursor.fetchall()
        return [row[0] for row in results]  # Return a list of achievement names
    except mysql.connector.Error as err:
        print(f"Error loading achievements: {err}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
