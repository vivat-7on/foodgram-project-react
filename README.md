ё# Документация для проекта Foodgram
 
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

## Установка и запуск

### Локальная установка:

1. Склонируйте репозиторий на вашу локальную машину:

    ```
    git clone git@github.com:vivat-7on/foodgram-project-react.git
    ```

2. Перейдите в папку с проектом:

    ```
    cd foodgram-project-react
    ```

3. Установите необходимые зависимости:

    ```
    pip install -r requirements.txt
    ```

4. Запустите проект:

    ```
    python manage.py runserver
    ```

### Установка на удаленный сервер (на примере Ubuntu):

1. Войдите на ваш удаленный сервер.

2. Установите Docker и Docker Compose:

    ```
    sudo apt install docker.io docker-compose
    ```

3. Локально отредактируйте файл `infra/nginx.conf`, заменив `server_name` на ваш IP.

4. Скопируйте файлы `docker-compose.yml` и `nginx.conf` на сервер:

    ```
    scp docker-compose.yml <username>@<host>:/path/to/destination
    scp nginx.conf <username>@<host>:/path/to/destination
    ```

5. Создайте файл `.env` и заполните необходимые переменные окружения, такие как `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY` и другие.

6. Соберите и запустите Docker Compose:

    ```
    sudo docker-compose up -d --build
    ```

## Доступ в интернете

После успешного запуска проекта он будет доступен по вашему IP-адресу.

## Окончание

Это описание поможет вам установить и запустить проект Foodgram локально или на удаленном сервере. Если у вас возникнут вопросы, не стесняйтесь обращаться к документации или сообществу разработчиков. Успехов в работе с проектом!

## Проект в интернете
Проект запущен и доступен по [адресу](https://food-gram.zapto.org/)
