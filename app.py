import streamlit as st
import psycopg2
from utils import auth, admin
from utils.helpers import require_role
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def load_books(search_term=None):
    """Загрузка книг из базы данных с учетом поиска, включая возрастную категорию."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    if search_term:
        cursor.execute("""
            SELECT b.book_id, b.title, b.date, b.author_id, b.description, b.number_of_likes, b.number_of_comments, b.book_cover, 
                   ac.category_characteristic 
            FROM books b
            LEFT JOIN age_categories_of_books acb ON b.book_id = acb.book_id
            LEFT JOIN age_category ac ON ac.age_id = acb.age_id
            WHERE b.title ILIKE %s
        """, (f'%{search_term}%',))
    else:
        cursor.execute("""
            SELECT b.book_id, b.title, b.date, b.author_id, b.description, b.number_of_likes, b.number_of_comments, b.book_cover, 
                   ac.category_characteristic 
            FROM books b
            LEFT JOIN age_categories_of_books acb ON b.book_id = acb.book_id
            LEFT JOIN age_category ac ON ac.age_id = acb.age_id
        """)
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return books

def load_comments(book_id):
    """Загрузка комментариев к книге из базы данных."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, comment_text, date FROM comments WHERE book_id = %s ORDER BY date DESC", (book_id,))
    comments = cursor.fetchall()
    cursor.close()
    connection.close()
    return comments

def add_comment(book_id, user_id, comment_text):
    """Добавление нового комментария к книге."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO comments (book_id, user_id, comment_text, date) VALUES (%s, %s, %s, NOW())", (book_id, user_id, comment_text,))
    connection.commit()
    cursor.close()
    connection.close()

def load_authors(search_term=None):
    """Загрузка авторов из базы данных с учетом поиска."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    if search_term:
        cursor.execute("SELECT author_id, fullname, biography FROM authors WHERE fullname ILIKE %s", (f'%{search_term}%',))
    else:
        cursor.execute("SELECT author_id, fullname, biography FROM authors")
    authors = cursor.fetchall()
    cursor.close()
    connection.close()
    return authors

def load_user_favorites_books(user_id):
    """Загрузка любимых книг пользователя."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT b.book_id, b.title, b.book_cover 
        FROM liked_books lb 
        JOIN books b ON lb.book_id = b.book_id 
        WHERE lb.user_id = %s
    """, (user_id,))
    favorites = cursor.fetchall()
    cursor.close()
    connection.close()
    return favorites

def load_user_favorites_authors(user_id):
    """Загрузка любимых авторов пользователя."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT a.author_id, a.fullname 
        FROM liked_books lb 
        JOIN books b ON lb.book_id = b.book_id 
        JOIN authors a ON b.author_id = a.author_id 
        WHERE lb.user_id = %s
    """, (user_id,))
    favorites = cursor.fetchall()
    cursor.close()
    connection.close()
    return favorites

def load_book_text(book_id):
    """Загрузка текста книги по ID."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT book_text FROM book_texts WHERE book_id = %s", (book_id,))
    text = cursor.fetchone()
    cursor.close()
    connection.close()
    return text[0] if text else None

def add_like_to_book(user_id, book_id):
    """Добавить лайк к книге пользователем."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Проверка, поставлен ли уже лайк

    cursor.execute("SELECT COUNT(*) FROM liked_books WHERE user_id = %s AND book_id = %s", (user_id, book_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Если нет, то добавляем
        cursor.execute("INSERT INTO liked_books (user_id, book_id) VALUES (%s, %s)", (user_id, book_id,))
        cursor.execute("UPDATE books SET number_of_likes = number_of_likes + 1 WHERE book_id = %s", (book_id,))
        connection.commit()
        st.success("Вы поставили лайк на книгу!")
    else:
        st.warning("Вы уже поставили лайк на эту книгу.")

    cursor.close()
    connection.close()

def add_favorite_author(user_id, author_id):
    """Добавить автора в любимые."""
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Проверка, отмечен ли уже автор как любимый
    cursor.execute("SELECT COUNT(*) FROM liked_books WHERE user_id = %s AND book_id IN (SELECT book_id FROM books WHERE author_id = %s)", (user_id, author_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Если нет, то добавляем
        cursor.execute("INSERT INTO liked_books (user_id, book_id) SELECT %s, book_id FROM books WHERE author_id = %s", (user_id, author_id,))
        connection.commit()
        st.success("Авторы добавлены в ваши любимые!")
    else:
        st.warning("Эти авторы уже добавлены в ваши любимые.")

    cursor.close()
    connection.close()

def main():
    st.title("Онлайн Библиотека")

    # Создание страниц
    page = st.sidebar.selectbox("Выберите страницу", ["Login", "Register", "Books", "Authors", "Favorites", "Comments", "Admin"])

    if page == "Login":
        auth.login_page(DB_CONFIG)
    elif page == "Register":
        auth.register_page(DB_CONFIG)
    elif page == "Books":
        book_search = st.text_input("Поиск по книгам", "")
        books = load_books(book_search)
        book_page(books)
    elif page == "Authors":
        author_search = st.text_input("Поиск по авторам", "")
        authors = load_authors(author_search)
        author_page(authors)
    elif page == "Favorites":
        user_id = st.session_state.get("user_id")
        if user_id:
            favorites_books = load_user_favorites_books(user_id)
            favorites_authors = load_user_favorites_authors(user_id)
            favorites_page(favorites_books, favorites_authors)
        else:
            st.error("Сначала выполните вход.")
    elif page == "Comments":
        comments_page()
    elif page == "Admin":
        auth_user = auth.get_authenticated_user()
        if auth_user and auth_user['role'] == 'admin':
            admin.admin_page(DB_CONFIG)
        else:
            st.error("У вас нет доступа к этой странице.")

def book_page(books):
    """Отображение книг, возможности оставлять комментарии и показывать текст произведения."""
    for book in books:
        book_id, title, publication_date, author_id, description, number_of_likes, number_of_comments, book_cover, age_category = book
        
        st.subheader(title)
        
        # Убедитесь, что путь к изображению правильный
        book_cover_path = f"assets/images/{book_cover}"  # Команда, задающая правильный путь к изображению
        if os.path.exists(book_cover_path):
            st.image(book_cover_path)
        else:
            st.error(f"Изображение '{book_cover}' не найдено.")
        
        # Отображаем возрастную категорию
        st.write(f"Возрастной рейтинг: **{age_category}**")  # Выводим возрастную категорию

        # Отображаем описание книги
        st.write("Описание:")
        st.write(description)

        # Кнопка для отображения текста книги
        if st.button(f"Показать текст произведения для '{title}'"):
            book_text = load_book_text(book_id)  # Загрузка текста книги
            if book_text:
                st.write(book_text)
            else:
                st.error("Текст произведения не найден.")

        # Форма для добавления нового комментария
        user_id = st.session_state.get("user_id")
        if user_id:
            # Передаем уникальный key, используя book_id
            new_comment = st.text_area("Добавить комментарий:", "", key=f"comment_{book_id}")
            if st.button("Добавить", key=f"add_comment_{book_id}"):  # Уникальный ключ для кнопки
                if new_comment:
                    add_comment(book_id, user_id, new_comment)
                    st.success("Комментарий добавлен!")
                else:
                    st.error("Введите текст комментария.")
        else:
            st.warning("Пожалуйста, войдите в систему, чтобы оставить комментарий.")


def comments_page():
    """Страница, показывающая все комментарии."""
    st.header("Все комментарии")
    
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT b.title, c.comment_text, c.user_id, c.date FROM comments c JOIN books b ON c.book_id = b.book_id ORDER BY c.date DESC")
    comments = cursor.fetchall()
    
    if comments:
        for comment in comments:
            book_title, comment_text, user_id, comment_date = comment
            st.write(f"**Книга:** {book_title}")
            st.write(f"**Комментарий:** {comment_text} (User ID: {user_id}, Дата: {comment_date})")
            st.write("---")
    else:
        st.write("Комментариев пока нет.")
    
    cursor.close()
    connection.close()

def author_page(authors):
    """Отображение авторов."""
    st.subheader("Список авторов")
    if not authors:
        st.write("Авторы не найдены.")
    else:
        for author_id, fullname, biography in authors:  # Добавили biography
            st.write(f"- {fullname}")
            
            # Отображение биографии
            st.write("Биография:")
            st.write(biography if biography else "Информация о биографии отсутствует.")
            
            user_id = st.session_state.get("user_id")
            if user_id:
                if st.button(f"Добавить {fullname} в любимые", key=f"fav_{author_id}"):
                    add_favorite_author(user_id, author_id)
            else:
                st.warning("Войдите, чтобы добавлять авторов в любимые.")
            
            st.write("---")

def favorites_page(favorites_books, favorites_authors):
    """Отображение любимых книг и авторов пользователя."""
    st.subheader("Ваши любимые книги")
    if not favorites_books:
        st.write("У вас нет любимых книг.")
    else:
        for book_id, title, book_cover in favorites_books:
            st.image(f"assets/images/{book_cover}", width=100)
            st.write(f"**{title}**")
            st.write("---")
    
    st.subheader("Ваши любимые авторы")
    if not favorites_authors:
        st.write("У вас нет любимых авторов.")
    else:
        for author_id, fullname in favorites_authors:
            st.write(f"- {fullname}")
    st.write("---")

if __name__ == "__main__":
    main()
