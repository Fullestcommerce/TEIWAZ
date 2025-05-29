import pygame
import random
from noise import pnoise2
import json
import mysql.connector
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
                discovered BOOLEAN DEFAULT FALSE
            )
        """)

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



def save_game_to_db(save_id, seed, actor_pos, game_timer, inventory):
    connection = get_db_connection()
    try:
        #перевід id сейву. Нагадую, цей баг ми фіксили 5 годин ))))))
        if isinstance(save_id, str) and save_id.startswith("Slot "):
            save_id = int(save_id.split(" ")[1])  #інакше збереження буде кожен раз створювати новий рядок, а не переписувати старий
        cursor = connection.cursor()

        inventory_str = ",".join(inventory)  #для зручності читання переводимо інвентар в стрінгу

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
        save_name = f"Slot {save_id}"  #Id сейву

        #дебаг виводи для сейвів(нагадую, баг фіксився 5 годин)
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


def load_game_from_db(save_id):#як не дивно ця функція запрацювала з першого разу і я її далі не фіксив
    connection = get_db_connection()
    try:
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
            inventory = inventory_str.split(",") if inventory_str else []  #перевід інвентаря в стрінгу для зручності збереження
            print(f"Data loaded: seed={seed}, actor_pos={[actor_pos_x, actor_pos_y]}, game_timer={game_timer}, inventory={inventory}")
            return seed, [actor_pos_x, actor_pos_y], game_timer, inventory
        else:
            print(f"No save found for slot ID: {save_id}")
            #повертання дефолту якщо гравець завантажить пустий сейв
            return None, [0, 0], 0, []
    except mysql.connector.Error as err:
        print(f"Error loading game: {err}")
        return None, [0, 0], 0, []
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

        #при генерації того ж сіду треба очистити його струтури, інакше вони вже будуть досліджені і гра зламається
        cursor.execute("DELETE FROM objects WHERE seed = %s", (seed,))

        #перша тестова структура яка завжди генериться на одних кордах
        structures = [
            {"type": "crash_site", "x": 320, "y": 320}
        ]

        #Генерація інших структур
        random.seed(seed)#використання сіду забезпечує однаковий результат генерації, що дозволяє мати менші файли збереження
        num_ruins = random.randint(10, 16)
        num_charging_stations = random.randint(4, 6)
        num_fuel_depots = random.randint(4, 6)
        num_salvaged_parts = random.randint(8, 12)
        num_extraction_points = 1

        def random_position():
            return random.randint(0, MAP_WIDTH * TILE_SIZE), random.randint(0, MAP_HEIGHT * TILE_SIZE)

        #різноманітні об'єкти. Надалі є ідея добавити геймплейні елементи, але це фаза 2
        for _ in range(num_ruins):#добавити можливість бою з ворогами
            x, y = random_position()#в руїнах також будуть артефакти, за які в фінальній версії і даватимуть очки
            structures.append({"type": "ruins", "x": x, "y": y})

        #добавити зарядку батареї ГГ
        for _ in range(num_charging_stations):
            x, y = random_position()
            structures.append({"type": "charging_station", "x": x, "y": y})

        #В депо необхідно буде взяти топливо для зарядки батареї і завершення гри
        for _ in range(num_fuel_depots):
            x, y = random_position()
            structures.append({"type": "fuel_depot", "x": x, "y": y})

        #Біля запчастин можна буде відновити хп і патрони
        for _ in range(num_salvaged_parts):
            x, y = random_position()
            structures.append({"type": "salvaged_parts", "x": x, "y": y})

        #лока для завершення гри
        for _ in range(num_extraction_points):
            x, y = random_position()
            structures.append({"type": "extraction_point", "x": x, "y": y})

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
def render_exploration_map(screen, exploration_map, tile_size=32):
   
    for x, column in enumerate(exploration_map):
        for y, tile in enumerate(column):
            if tile == "floor":
                color = (200, 200, 200)  # Light gray for floor
            elif tile == "wall":
                color = (50, 50, 50)  # Dark gray for walls
            elif tile == "hole":
                color = (0, 0, 0)  # Black for holes
            else:
                color = (255, 0, 0)  # Red for unknown tiles (debugging)
            pygame.draw.rect(screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))

def generate_exploration_map(seed=None, width=64, height=64):
    if seed is None:
        seed = random.randint(0, 100)
    random.seed(seed)

    # Initialize the map with walls
    exploration_map = [["wall" for _ in range(height)] for _ in range(width)]

    def carve_room(x, y, w, h):
        """Carve out a rectangular room."""
        for i in range(x, x + w):
            for j in range(y, y + h):
                if 0 <= i < width and 0 <= j < height:
                    exploration_map[i][j] = "floor"

    def carve_corridor(x1, y1, x2, y2):
        """Carve out a corridor between two points."""
        if random.choice([True, False]):
            # Horizontal first, then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < width and 0 <= y1 < height:
                    exploration_map[x][y1] = "floor"
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x2 < width and 0 <= y < height:
                    exploration_map[x2][y] = "floor"
        else:
            # Vertical first, then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x1 < width and 0 <= y < height:
                    exploration_map[x1][y] = "floor"
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < width and 0 <= y2 < height:
                    exploration_map[x][y2] = "floor"

    # Generate rooms and corridors
    num_rooms = random.randint(8, 12)
    rooms = []
    for _ in range(num_rooms):
        room_width = random.randint(5, 10)
        room_height = random.randint(5, 10)
        room_x = random.randint(1, width - room_width - 1)
        room_y = random.randint(1, height - room_height - 1)
        carve_room(room_x, room_y, room_width, room_height)
        rooms.append((room_x + room_width // 2, room_y + room_height // 2))  # Store room center

    # Connect rooms with corridors
    for i in range(len(rooms) - 1):
        carve_corridor(rooms[i][0], rooms[i][1], rooms[i + 1][0], rooms[i + 1][1])

    # Add random holes (optional)
    num_holes = random.randint(5, 10)
    for _ in range(num_holes):
        hole_x = random.randint(0, width - 1)
        hole_y = random.randint(0, height - 1)
        exploration_map[hole_x][hole_y] = "hole"

    return exploration_map
