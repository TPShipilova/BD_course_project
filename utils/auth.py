import streamlit as st
import bcrypt
import psycopg2

def connect_to_db(DB_CONFIG):
    """Подключение к базе данных."""
    return psycopg2.connect(**DB_CONFIG)

def login_page(DB_CONFIG):
    """Страница входа в систему."""
    st.header("Вход в систему")

    email = st.text_input("Введите ваш email", "")
    password = st.text_input("Введите ваш пароль", "", type='password')

    if st.button("Войти"):
        connection = connect_to_db(DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, hash_password, role FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
            st.session_state["user_id"] = result[0]
            st.session_state["role"] = result[2]
            st.success("Вход выполнен успешно!")
        else:
            st.error("Неверный email или пароль.")

def register_page(DB_CONFIG):
    """Страница регистрации пользователя."""
    st.header("Регистрация")

    email = st.text_input("Введите ваш email", "")
    password = st.text_input("Введите ваш пароль", "", type='password')

    age = st.number_input("Ваш возраст", min_value=0)

    if st.button("Зарегистрироваться"):
        connection = connect_to_db(DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        count = cursor.fetchone()[0]

        if count > 0:
            st.error("Этот email уже зарегистрирован.")
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (email, hash_password, age) VALUES (%s, %s, %s)",
                (email, hashed_password, age)
            )
            connection.commit()
            cursor.close()
            connection.close()
            st.success("Регистрация прошла успешно!")

def get_authenticated_user():
    """Получить аутентифицированного пользователя."""
    return {
        'user_id': st.session_state.get("user_id"),
        'role': st.session_state.get("role"),
    }
