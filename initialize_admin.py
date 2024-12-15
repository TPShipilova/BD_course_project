# запустить 1 раз

import bcrypt
import psycopg2
import os
from dotenv import load_dotenv


# Загружаем переменные окружения из .env файла
load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_ROLE = os.getenv("ADMIN_ROLE")

def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return connection
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None

def initialize_admin():
    """Добавление администратора в базу данных."""
    connection = connect_to_db()
    if not connection:
        return

    try:
        cursor = connection.cursor()
        # Проверяем, существует ли администратор
        cursor.execute("SELECT COUNT(*) FROM Users WHERE email = %s", (ADMIN_EMAIL,))
        count = cursor.fetchone()[0]
        if count > 0:
            print("Администратор уже существует в базе данных.")
        else:
            # Генерация хэша пароля
            hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # Вставка данных администратора
            cursor.execute(
                "INSERT INTO Users (email, hash_password, role, age) VALUES (%s, %s, %s, %s)",
                (ADMIN_EMAIL, hashed_password, ADMIN_ROLE, 20)
            )
            connection.commit()
            print("Администратор успешно добавлен.")
        cursor.close()
    except Exception as e:
        print(f"Ошибка добавления администратора: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    initialize_admin()
