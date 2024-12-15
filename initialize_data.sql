-- Таблица пользователей
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INT NOT NULL,
    role VARCHAR(50),
    hash_password VARCHAR(255) NOT NULL
);

-- Таблица авторов
CREATE TABLE IF NOT EXISTS Authors (
    author_id SERIAL PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    biography TEXT
);

-- Таблица книг
CREATE TABLE IF NOT EXISTS Books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    author_id INT NOT NULL,
    description TEXT,
    number_of_likes INT DEFAULT 0,
    number_of_comments INT DEFAULT 0,
    book_cover VARCHAR(255),
    FOREIGN KEY (author_id) REFERENCES Authors(author_id)
);

-- Таблица возрастных категорий
CREATE TABLE IF NOT EXISTS Age_Category (
    age_id SERIAL PRIMARY KEY,
    age VARCHAR(50) NOT NULL, -- возрастной диапазон
    category_characteristic TEXT NOT NULL
);

-- Множество книг и возрастных категорий
CREATE TABLE IF NOT EXISTS Age_Categories_of_Books (
    book_id INT NOT NULL,
    age_id INT NOT NULL,
    PRIMARY KEY (book_id, age_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (age_id) REFERENCES Age_Category(age_id)
);

-- Таблица liked_books
CREATE TABLE IF NOT EXISTS Liked_Books (
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    PRIMARY KEY (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

-- Таблица комментариев
CREATE TABLE IF NOT EXISTS Comments (
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, user_id, date),
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Таблица жанров
CREATE TABLE IF NOT EXISTS Genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(255) NOT NULL
);

-- Множество книг и жанров
CREATE TABLE IF NOT EXISTS Book_Genres (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

-- Таблица текстов книг
CREATE TABLE IF NOT EXISTS Book_Texts (
    book_id INT NOT NULL,
    book_text TEXT NOT NULL,
    PRIMARY KEY (book_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

-- Тестовые данные для пользователей
INSERT INTO Users (email, age, role, hash_password)
VALUES
('user1@example.com', 20, 'viewer', 'hashed_password'),
('user2@example.com', 25, 'viewer', 'hashed_password'),
('user3@example.com', 20, 'viewer', 'hashed_password'),
('user4@example.com', 25, 'viewer', 'hashed_password');

-- Тестовые данные для авторов
INSERT INTO Authors (author_id, fullname, biography) VALUES
(1, 'Александр Пушкин', 'Русский поэт, драматург и прозаик.'),
(2, 'Анна Ахматова', 'Русская поэтесса, одна из самых значительных фигур русской литературы XX века.');

-- Тестовые данные для книг
INSERT INTO Books (title, date, author_id, description, book_cover) VALUES
('Я вас любил', '1833-01-01', 1, 'Стихотворение о любви.', 'ya_vas_lyubil.jpg'),
('Сон', '1944-01-01', 2, 'Грустное стихотворение о раздумьях.', 'son.jpg');

-- Тестовые данные для возрастных категорий
INSERT INTO Age_Category (age, category_characteristic) VALUES
('0-6', 'Книги для самых маленьких читателей.'),
('7-12', 'Книги для детей школьного возраста.'),
('13-17', 'Подростковые книги.'),
('18+', 'Книги для взрослых.');


-- Связи возрастных категорий и книг
INSERT INTO Age_Categories_of_Books (book_id, age_id) VALUES
(1, 1),  -- Я вас любил - Для детей
(2, 4);  -- Сон - Для взрослых

-- Тестовые данные для жанров
INSERT INTO Genres (genre_name) VALUES
('Лирика'),
('Драма');

-- Связь книг и жанров
INSERT INTO Book_Genres (book_id, genre_id) VALUES
(1, 1), -- Я вас любил - Лирика
(2, 1); -- Сон - Лирика

-- Тестовые данные для текстов книг
INSERT INTO Book_Texts (book_id, book_text) VALUES
(1, 'Я вас любил: любовь ещё, быть может, в душе моей угасла не совсем.'),
(2, 'Сон, как светлое озеро, пусто, и в бездне линии...');

-- Тестовые данные для комментариев
INSERT INTO Comments (book_id, user_id, comment_text, date) VALUES
(1, 1, 'Прекрасное стихотворение!'),
(2, 2, 'Грустно, но очень красиво!');



