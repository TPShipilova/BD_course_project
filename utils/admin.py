import streamlit as st
import psycopg2
import os
import subprocess

def connect_to_db(db_config):
    """Подключение к базе данных с использованием переданных данных"""
    try:
        connection = psycopg2.connect(
            host=db_config['host'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        return connection
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None

def admin_page(DB_CONFIG):
    """Панель администратора."""
    st.title("Панель администратора")

    if st.sidebar.checkbox("Создать резервную копию базы данных"):
        create_db_backup(DB_CONFIG)
    if st.sidebar.checkbox("Добавить новую книгу"):
        add_book(DB_CONFIG)
    if st.sidebar.checkbox("Удалить книгу"):
        delete_book(DB_CONFIG)
    if st.sidebar.checkbox("Добавить нового автора"):
        add_author(DB_CONFIG)

def create_db_backup(DB_CONFIG):
    """Создание резервной копии базы данных."""
    st.subheader("Создание резервной копии базы данных")
    backup_file_name = st.text_input("Введите имя файла для бекапа (без расширения)", "backup")

    if st.button("Создать бекап"):
        if not backup_file_name:
            st.error("Пожалуйста, введите имя файла.")
        else:
            backup_file_path = os.path.join("backups", f"{backup_file_name}.sql")

            # Создаем директорию для бекапов, если она не существует
            if not os.path.exists("backups"):
                os.makedirs("backups")

            # Формируем команду для создания бекапа
            try:
                command = [
                    "pg_dump",
                    "-h", DB_CONFIG['host'],          # Хост базы данных
                    "-U", DB_CONFIG['user'],          # Пользователь базы данных
                    "-d", DB_CONFIG['database'],      # Имя базы данных
                    "-f", backup_file_path             # Путь к файлу бекапа
                ]
                
                # Передаем пароль через PGPASSWORD
                env = os.environ.copy()
                env["PGPASSWORD"] = DB_CONFIG['password']

                # Выполняем команду
                subprocess.run(command, check=True, env=env)

                st.success(f"Бекап успешно создан: {backup_file_path}")

            except subprocess.CalledProcessError as e:
                st.error(f"Ошибка при создании бекапа: {e}")
            except Exception as e:
                st.error(f"Неизвестная ошибка: {e}")

def add_book(DB_CONFIG):
    """Добавление новой книги."""
    st.subheader("Добавление новой книги")

    title = st.text_input("Название книги")
    
    authors = get_authors(DB_CONFIG)
    author_names = [author.split(": ")[1] for author in authors]
    author_ids = [author.split(": ")[0] for author in authors]

    author_id = st.selectbox("Выберите автора", author_names)
    author_id = author_ids[author_names.index(author_id)]

    description = st.text_area("Описание книги")
    book_cover = st.text_input("Название файла обложки (в assets/images/)")
    date = st.date_input("Дата публикации")
    text = st.text_area("Текст книги")

    # Выбор возрастной категории
    age_categories = get_age_categories(DB_CONFIG)
    age_names = [category[1] for category in age_categories]  # category_characteristic
    age_ids = [category[0] for category in age_categories]  # age_id
    age_id = st.selectbox("Выберите возрастной рейтинг", age_names)

    # Получаем выбранный age_id
    age_id = age_ids[age_names.index(age_id)]

    if st.button("Добавить книгу"):
        connection = connect_to_db(DB_CONFIG)
        cursor = connection.cursor()
        
        # Вставка новой книги
        cursor.execute(
            "INSERT INTO books (title, date, author_id, description, book_cover) VALUES (%s, %s, %s, %s, %s)",
            (title, date, author_id, description, book_cover)
        )

        # Получаем ID добавленной книги
        cursor.execute("SELECT book_id FROM books WHERE title = %s", (title,))
        book_id = cursor.fetchone()[0]

        if text:
            cursor.execute("INSERT INTO book_texts (book_id, book_text) VALUES (%s, %s)", (book_id, text))

        # Запись связи между книгой и возрастным рейтингом
        cursor.execute(
            "INSERT INTO age_categories_of_books (book_id, age_id) VALUES (%s, %s)",
            (book_id, age_id)
        )

        connection.commit()
        cursor.close()
        connection.close()
        st.success(f"Книга '{title}' успешно добавлена!")        

def get_age_categories(DB_CONFIG):
    """Загрузка возрастных категорий из базы данных."""
    connection = connect_to_db(DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT age_id, category_characteristic FROM age_category")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()
    return categories

def delete_book(DB_CONFIG):
    """Удаление книги."""
    st.subheader("Удаление книги")

    books = load_books(DB_CONFIG)
    book_id = st.selectbox("Выберите книгу для удаления", [book[0] for book in books])

    # Проверка, есть ли книга в избранном
    connection = connect_to_db(DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM liked_books WHERE book_id = %s", (book_id,))
    in_favorites_count = cursor.fetchone()[0]
    cursor.close()
    connection.close()

    if in_favorites_count > 0:
        st.warning("Эта книга есть в избранном у пользователей. Убедитесь, что хотите удалить её.")
        confirm = st.button("Подтвердить удаление книги и из избранного")

        if confirm:
            # Подключаемся к базе данных
            connection = connect_to_db(DB_CONFIG)
            cursor = connection.cursor()

            # Удаляем все тексты, связанные с книгой
            cursor.execute("DELETE FROM book_texts WHERE book_id = %s", (book_id,))

            # Удаляем книгу из таблицы liked_books
            cursor.execute("DELETE FROM liked_books WHERE book_id = %s", (book_id,))

            # Удаляем книгу из основного списка
            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            connection.commit()
            cursor.close()
            connection.close()

            st.success(f"Книга с ID '{book_id}' успешно удалена, включая избранное!")
    else:
        if st.button("Удалить книгу"):
            # Подключаемся к базе данных
            connection = connect_to_db(DB_CONFIG)
            cursor = connection.cursor()

            # Удаляем все тексты, связанные с книгой
            cursor.execute("DELETE FROM book_texts WHERE book_id = %s", (book_id,))

            # Удаляем книгу из основного списка
            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            connection.commit()
            cursor.close()
            connection.close()

            st.success(f"Книга с ID '{book_id}' успешно удалена!")



def add_author(DB_CONFIG):
    """Добавление нового автора."""
    st.subheader("Добавление нового автора")

    fullname = st.text_input("Полное имя автора")
    biography = st.text_area("Биография автора")

    if st.button("Добавить автора"):
        connection = connect_to_db(DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO authors (fullname, biography) VALUES (%s, %s)",
            (fullname, biography)
        )
        connection.commit()
        cursor.close()
        connection.close()
        st.success(f"Автор '{fullname}' успешно добавлен!")

def get_authors(DB_CONFIG):
    """Получение списка авторов для выбора."""
    connection = connect_to_db(DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT author_id, fullname FROM authors")
    authors = cursor.fetchall()
    cursor.close()
    connection.close()
    return [f"{author[0]}: {author[1]}" for author in authors]

def load_books(DB_CONFIG):
    """Загрузка книг из базы данных для удаления."""
    connection = connect_to_db(DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT book_id, title FROM books")
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return books
