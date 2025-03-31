CREATE DATABASE teiwaz_game;

USE teiwaz_game;

CREATE TABLE saves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    save_name VARCHAR(255) NOT NULL,
    seed INT NOT NULL,
    actor_pos_x FLOAT NOT NULL,
    actor_pos_y FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);