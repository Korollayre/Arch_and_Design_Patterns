PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS categories;
CREATE TABLE categories
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR(50) UNIQUE
);

DROP TABLE IF EXISTS games;
CREATE TABLE games
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR(50) UNIQUE,
    description TEXT,
    price INTEGER,
    release_date DATE
);

DROP TABLE IF EXISTS games_categories;
CREATE TABLE games_categories
(
    game_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (game_id, category_id),
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)

);

DROP TABLE IF EXISTS categories_dependence;
CREATE TABLE categories_dependence
(
    main_category_id INTEGER NOT NULL,
    sub_category_id INTEGER NOT NULL,
    PRIMARY KEY (main_category_id, sub_category_id),
    FOREIGN KEY (main_category_id) REFERENCES categories(id),
    FOREIGN KEY (sub_category_id) REFERENCES categories(id)
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = OFF;
