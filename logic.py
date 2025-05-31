import pygame
import random
from noise import pnoise2
import json
import mysql.connector
import heapq  # For priority queue
#Тут зараз буде 400 рядків чистого хаосу і години моєї праці
TILE_SIZE=32
MAP_WIDTH=300 
MAP_HEIGHT=300
SCALE=100
def get_db_connection():
    #Функція підключення датабази(за вашим спецзамовленням)
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="teiwaz_game"
        )
        return connection
    #добавив кондицію на помилку, також працюватиме як хороший дебаг в випадку
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        return None
def setup_database():
    connection = get_db_connection()
    if not connection:#failsave на випадок помилки підключення
        return
    try:
        cursor = connection.cursor()

        #чек датабази і її створення якщо її німа
        cursor.execute("CREATE DATABASE IF NOT EXISTS teiwaz_game")
        cursor.execute("USE teiwaz_game")

        #сіквенс на створення таблиць
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

        #об'єкти
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                object_type VARCHAR(255) NOT NULL,
                pos_x INT NOT NULL,
                pos_y INT NOT NULL,
                seed INT NOT NULL,
                discovered BOOLEAN DEFAULT FALSE,
                discovered_1 BOOLEAN DEFAULT FALSE,
                discovered_2 BOOLEAN DEFAULT FALSE,
                discovered_3 BOOLEAN DEFAULT FALSE
            )
        """)
        cursor.execute("SHOW COLUMNS FROM objects LIKE 'discovered_1'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE objects ADD COLUMN discovered_1 BOOLEAN DEFAULT FALSE")

        cursor.execute("SHOW COLUMNS FROM objects LIKE 'discovered_2'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE objects ADD COLUMN discovered_2 BOOLEAN DEFAULT FALSE")

        cursor.execute("SHOW COLUMNS FROM objects LIKE 'discovered_3'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE objects ADD COLUMN discovered_3 BOOLEAN DEFAULT FALSE")

        #Ачівки
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,  -- Achievement name must be unique
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of when the achievement was unlocked
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL     
    )
""")
        #дефолтні юзери, щоб не вводити кожен раз з нуля
        default_users = [
            ("developer", "dungeonmaster123"),
            ("anatoli", "pas1"),
            ("vova", "pas2")
        ]
        for username, password in default_users:
            cursor.execute("""
                INSERT IGNORE INTO users (username, password)
                VALUES (%s, %s)
            """, (username, password))

        #АЧІВКИ!
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
def validate_login(username, password):
    """Validate the username and password against the database."""
    connection = get_db_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return result[0] > 0  #повертає 1 якщо ми залогінилися. ІНАКШЕ НІ
    except mysql.connector.Error as err:
        print(f"Error validating login: {err}")
        return False
    finally:
        if connection.is_connected():
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
        obj_image = pygame.image.load(f"assets/{obj['type']}.png")  
        screen.blit(obj_image, (obj["x"] - camera_x, obj["y"] - camera_y)) 

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



def save_game_to_db(save_id, seed, actor_pos, game_timer, inventory, objects):
    connection = get_db_connection()
    try:
        if isinstance(save_id, str) and save_id.startswith("Slot "):
            save_id = int(save_id.split(" ")[1])
        cursor = connection.cursor()

        inventory_str = ",".join(inventory)

        # Save the game state
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
        save_name = f"Slot {save_id}"
        cursor.execute(query, (save_id, save_name, seed, actor_pos[0], actor_pos[1], game_timer, inventory_str))

        # Update the discovered_<slot> column for the current seed
        discovered_column = f"discovered_{save_id}"
        query = f"""
            UPDATE objects
            SET {discovered_column} = discovered
            WHERE seed = %s
        """
        cursor.execute(query, (seed,))

        connection.commit()
        print(f"Game saved successfully to slot ID: {save_id}")
    except mysql.connector.Error as err:
        print(f"Error saving game: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def load_game_from_db(save_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        # Load the game state
        query = """
            SELECT seed, actor_pos_x, actor_pos_y, game_timer, inventory
            FROM saves
            WHERE id = %s
        """
        print(f"Loading from slot ID: {save_id}")
        cursor.execute(query, (save_id,))
        result = cursor.fetchone()
        if result:
            seed, actor_pos_x, actor_pos_y, game_timer, inventory_str = result
            inventory = inventory_str.split(",") if inventory_str else []

            # Update the discovered column for the current seed
            discovered_column = f"discovered_{save_id}"
            query = f"""
                UPDATE objects
                SET discovered = {discovered_column}
                WHERE seed = %s
            """
            print(f"Executing query: {query} with seed: {seed}")
            cursor.execute(query, (seed,))

            # Load objects for the seed
            objects = load_objects_from_db(seed)

            print(f"Data loaded: seed={seed}, actor_pos={[actor_pos_x, actor_pos_y]}, game_timer={game_timer}, inventory={inventory}")
            return seed, [actor_pos_x, actor_pos_y], game_timer, inventory, objects
        else:
            print(f"No save found for slot ID: {save_id}")
            return None, [0, 0], 0, [], []
    except mysql.connector.Error as err:
        print(f"Error loading game: {err}")
        return None, [0, 0], 0, [], []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def list_saves():
    connection=get_db_connection()
    try:
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
    connection=get_db_connection()
    try:
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
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        query = "SELECT id, object_type, pos_x, pos_y, discovered FROM objects WHERE seed = %s"
        cursor.execute(query, (seed,))
        objects = cursor.fetchall()
        return [{"id": obj[0], "type": obj[1], "x": obj[2], "y": obj[3], "discovered": obj[4]} for obj in objects]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_structures(seed):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        # Clear existing structures for the seed
        cursor.execute("DELETE FROM objects WHERE seed = %s", (seed,))

        # Define location types and their counts
        location_types = [
            ("depot_ruins", random.randint(4, 6)),
            ("stockpile_ruins", random.randint(3, 5)),
            ("lab_ruins", random.randint(2, 3)),
            ("extraction_point", 1)
        ]

        structures = []
        random.seed(seed)

        def random_position():
            return random.randint(0, MAP_WIDTH * TILE_SIZE), random.randint(0, MAP_HEIGHT * TILE_SIZE)

        # Generate structures based on location types
        for location_type, count in location_types:
            for _ in range(count):
                x, y = random_position()
                structures.append({"type": location_type, "x": x, "y": y})

        debug_structures = [
            {"type": "small_location", "x": TILE_SIZE * 5, "y": TILE_SIZE * 5},
            {"type": "depot_ruins", "x": TILE_SIZE * 10, "y": TILE_SIZE * 10},
            {"type": "stockpile_ruins", "x": TILE_SIZE * 15, "y": TILE_SIZE * 15},
            {"type": "lab_ruins", "x": TILE_SIZE * 20, "y": TILE_SIZE * 20},
            {"type": "extraction_point", "x": TILE_SIZE * 25, "y": TILE_SIZE * 25},
        ]
        structures.extend(debug_structures)
        # Save structures to the database
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

    #чек ачівок
    if score > 1000:
        achievement = "High Score: Reach a score higher than 1000"
        achievements.append(achievement)
        save_achievement_to_db(achievement)

    if game_timer < 180:
        achievement = "Speed Runner: Finish the game in under 180 seconds"
        achievements.append(achievement)
        save_achievement_to_db(achievement)

    if not inventory:
        achievement = "Minimalist: Finish the game with an empty inventory"
        achievements.append(achievement)
        save_achievement_to_db(achievement)

    return list(set(achievements))  #видалення дублікатів(а вони будуть)

def save_achievement_to_db(achievement_name):
    connection = get_db_connection()
    try:
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
#для коміту
def load_achievements_from_db():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        query = "SELECT name FROM achievements"
        cursor.execute(query)
        results = cursor.fetchall()
        return [row[0] for row in results] 
    except mysql.connector.Error as err:
        print(f"Error loading achievements: {err}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
def mark_object_as_discovered(object_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        query = "UPDATE objects SET discovered = TRUE WHERE id = %s"
        cursor.execute(query, (object_id,))
        connection.commit()
        print(f"Object with ID {object_id} marked as discovered.")
    except mysql.connector.Error as err:
        print(f"Error updating object: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
def generate_random_map(width, height, location_type):
    """Generate a random map with rooms and corridors based on location type."""
    if location_type not in LOCATION_PROPERTIES:
        return [[1 for _ in range(width)] for _ in range(height)], []  # Default to walls

    props = LOCATION_PROPERTIES[location_type]
    num_rooms = props["num_rooms"]
    max_room_size = props["max_room_size"]
    min_room_size = props["min_room_size"]

    game_map = [[1 for _ in range(width)] for _ in range(height)]
    rooms = []

    def create_room(x, y, w, h):
        """Carve out a rectangular room."""
        for i in range(y, y + h):
            for j in range(x, x + w):
                if 0 <= i < height and 0 <= j < width:
                    game_map[i][j] = 0

    def create_corridor(x1, y1, x2, y2):
        """Carve out a corridor between two points."""
        if random.choice([True, False]):
            # Horizontal first, then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                game_map[y1][x] = 0
            for y in range(min(y1, y2), max(y1, y2) + 1):
                game_map[y][x2] = 0
        else:
            # Vertical first, then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                game_map[y][x1] = 0
            for x in range(min(x1, x2), max(x1, x2) + 1):
                game_map[y2][x] = 0

    # Generate random rooms
    for _ in range(num_rooms):
        room_width = random.randint(min_room_size, max_room_size)
        room_height = random.randint(min_room_size, max_room_size)
        room_x = random.randint(1, width - room_width - 1)
        room_y = random.randint(1, height - room_height - 1)

        new_room = (room_x, room_y, room_width, room_height)
        rooms.append(new_room)
        create_room(room_x, room_y, room_width, room_height)

    # Connect rooms with corridors
    for i in range(1, len(rooms)):
        x1, y1 = rooms[i - 1][0] + rooms[i - 1][2] // 2, rooms[i - 1][1] + rooms[i - 1][3] // 2
        x2, y2 = rooms[i][0] + rooms[i][2] // 2, rooms[i][1] + rooms[i][3] // 2
        create_corridor(x1, y1, x2, y2)

    return game_map, rooms

LOCATION_PROPERTIES = {
    "small_location": {
        "num_rooms": 5,
        "max_room_size": 6,
        "min_room_size": 3,
        "enemies": []  # No enemies
    },
    "depot_ruins": {
        "num_rooms": 8,
        "max_room_size": 8,
        "min_room_size": 4,
        "enemies": [("drone", 5), ("robot", 2)]  # 5 drones, 2 robots
    },
    "stockpile_ruins": {
        "num_rooms": 10,
        "max_room_size": 10,
        "min_room_size": 5,
        "enemies": [("drone", 7), ("robot", 3)]  # 7 drones, 3 robots
    },
    "lab_ruins": {
        "num_rooms": 15,
        "max_room_size": 12,
        "min_room_size": 6,
        "enemies": [("drone", 10), ("robot", 5), ("sentry", 3)]  # All enemy types
    },
    "extraction_point": {
        "num_rooms": 15,
        "max_room_size": 12,
        "min_room_size": 6,
        "enemies": [("drone", 12), ("robot", 6), ("sentry", 4)]  # More enemies
    }
}

def heuristic(a, b):
    """Heuristic function for A* (Manhattan distance)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(game_map, start, goal):
    """A* pathfinding algorithm."""
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Up, Right, Down, Left
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(game_map[0]) and 0 <= neighbor[1] < len(game_map):
                if game_map[neighbor[1]][neighbor[0]] == 1:  # Wall
                    continue

                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

