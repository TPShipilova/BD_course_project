# BD_course_project
Итоговый проект по курсу "Базы данных", 5 семестр

В данном репозитории представлен код на языке Python. Чтобы запустить локально, используйте dotenv, запишите туда ваши данные о базе данных в данном формате:

```
   # .env файл
   DB_HOST=<your_host>
   DB_DATABASE=<ur_database>
   DB_USER=<user_name>
   DB_PASSWORD=<password>

   ADMIN_EMAIL=<admin_male>
   ADMIN_PASSWORD=<admin_password>
   ADMIN_ROLE=<admin_role>
```

Убедитесь, что подключение выполнено.

Далее используйте скрипт initial_data.sql, затем initialize_admin.py.

После этого проверьте настройки виртуального окружения, установите необходимые библиотеки - они указаны в начале некоторых файлов. 

Чтобы запустить проект, используйте streamlit run app.py
