# Проект Foodgram
**Это приложение позволяет создавать, просматривать, удалять рецепты, подписываться на рецепты различных авторов, добавлять рецепты в избранное, добавлять рецепты в список покупок и формировать список покупок для всех ингредиентов добавленных в список в формате pdf**

## Возможности Foodgram:
* Аутентификация по токену
* Получение списка рецептов, просмотр рецептов, создание, изменение и удаление рецептов авторизованным пользователем
* Подписка на рецепты другого пользователя
* Добавление рецептов в список избранного
* Добавление рецептов в список покупок и скачивание pdf файла со списком ингредиентов для рецептов из списка покупок
* Поиск ингредиентов по названию
* Поиск рецептов по тэгам


## Деплой проекта

Проект можно развернуть при помощи Docker образов: 

Создаем директорию проекта и заходим в неё (заменить project_name на название проекта)
*mkdir <project_name>*
*mkdir <cd>*

Копируем файл docker-compose.production.yml в папку с проектом 
*scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/<project_name>/docker-compose.production.yml*
    
Выполняет pull образов с Docker Hub
*sudo docker compose -f docker-compose.production.yml pull*
Перезапускаем все контейнеры в Docker Compose
*sudo docker compose -f docker-compose.production.yml down*
*sudo docker compose -f docker-compose.production.yml up -d*

Выполняем миграции и сбор статики
*sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate*
*sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic*
*sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/static_django/. /static*


## Примеры запросов:

GET
*/api/recipes/*
Получить список всех рецептов. При указании параметров page и limit выдача будет с пагинацией.

POST
*/api/recipes/*
Добавление нового рецепта. Доступно только для аутентифицированного пользователя

GET
*/api/recipes/{id}*
Получение рецепта по id.

PATCH, DELETE
*/api/recipes/{id}*
Изменение, удаление рецепта только его автором

GET
*/api/users/me*
Просмотр своего профиля

GET
*/api/recipes/download_shopping_cart*
Скачивание pdf файла с ингредиентами для рецептов из списка покупок


Автор: Сергей Екшевиц

Используемые технологии:

Python 3.9,
Django 4.2.7, Django Rest Framework
Djoser
React
PostreSQL
