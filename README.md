# Документация для проекта Foodgram
 
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)


## О проекте

Foodgram - это веб-приложение, разработанное для обмена рецептами. Пользователи могут создавать аккаунты, подписываться на других авторов, добавлять рецепты в избранное и список покупок, а также загружать список покупок для рецептов.

Для реализации проекта была спроектированна следующая база данных:

<img width="880" alt="Снимок экрана 2024-05-23 в 18 10 42" src="https://github.com/vivat-7on/foodgram-project-react/assets/124658891/a2749478-aeec-4a34-bd80-733e6c6a9c94">


## Установка и запуск

### Локальная установка:

1. Создайте виртуальное окружение для проекта. Воспользуйтесь вашим предпочтительным инструментом для создания виртуального окружения. Например, с использованием `venv`:

    ```
    python -m venv venv
    ```

2. Активируйте виртуальное окружение:

    - На Windows:
    
    ```
    venv\Scripts\activate
    ```

    - На macOS и Linux:
    
    ```
    source venv/bin/activate
    ```

3. Склонируйте репозиторий на вашу локальную машину:

    ```
    git clone git@github.com:vivat-7on/foodgram-project-react.git
    ```

4. Перейдите в папку с проектом:

    ```
    cd foodgram-project-react
    ```

5. Установите необходимые зависимости:

    ```
    pip install -r requirements.txt
    ```

6. Выполните миграции:

    ```
    python manage.py migrate
    ```

7. Создайте суперпользователя:

    ```
    python manage.py createsuperuser
    ```

8. Запустите сервер:

    ```
    python manage.py runserver
    ```
## Запуск проекта в Docker

1. Убедитесь, что у вас установлен Docker и Docker Compose.

2. Склонируйте репозиторий на вашу локальную машину:

    ```
    git clone git@github.com:vivat-7on/your-project.git
    ```

3. Перейдите в папку с проектом:

    ```
    cd your-project
    ```

4. Создайте файл `.env` в корне проекта и заполните его переменными окружения, необходимыми для настройки проекта. Например:

    ```
    SECRET_KEY=<your_django_secret_key>
    DEBUG=False
    ALLOWED_HOSTS=<your_ip_or_domen>,localhost,127.0.0.1
    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_HOST=db
    DB_PORT=5432
    ```

5. Находясь в корне проекта апустите Docker Compose для создания и запуска всех контейнеров:

    ```
    docker-compose up --build
    ```

6. После успешного запуска всех контейнеров откройте браузер и перейдите по адресу http://localhost:8000/, чтобы убедиться, что ваш проект работает корректно.

7. Чтобы остановить работу контейнеров, выполните:

    ```
    docker-compose down
    ```


### Установка на удаленный сервер (на примере Ubuntu):

1. Войдите на ваш удаленный сервер.

2. Установите Docker и Docker Compose:

    ```
    sudo apt install docker.io docker-compose
    ```

3. Создайте файл `.env` и заполните необходимые переменные окружения, такие как `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY` и другие.

4. Скопируйте файлы `docker-compose-prodaction.yml` на сервер:

    ```
    scp docker-compose.yml <username>@<host>:/path/to/destination
    ```

5. Соберите и запустите Docker Compose:

    ```
    sudo docker-compose up -d --build
    ```

6. Установите Nginx на сервер:

    ```
    sudo apt install nginx
    ```

7. Отредактируйте конфигурационный файл Nginx для вашего проекта. Создайте новый файл конфигурации в директории `/etc/nginx/sites-available/` (например, `your_project.conf`) и добавьте в него следующее содержимое, заменив `<your_domain_or_ip>` на ваш домен или IP-адрес:

    ```
    server {
        server_name <your_domain_or_ip>;

        location / {
            proxy_set_header Host $host;
            proxy_pass http://localhost:8000;
        }
    }
    ```

8.  Протестируйте nginx:
    ```
    sudo nginx -t
    ```

9. Перезапустите Nginx для применения изменений:

    ```
    sudo systemctl restart nginx
    ```

## Доступ в интернете

После успешного запуска проекта он будет доступен по вашему домену или IP-адресу.
