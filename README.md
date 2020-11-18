https://github.com/jlllk/yamdb_final/workflows/yamdb_workflow/badge.svg
# YaMDb

YaMDb — веб-сайт о кинематографе, на котором пользователи могут оставлять оценки и отзывы к фильмам и сериалам.

## Зависимости

Установите Docker с [официального сайта](https://www.docker.com/).

## Запуск сервиса

Убедитесь, что Docker установлен и запущен.

Склонируйте репозиторий 
```
git clone https://github.com/jlllk/api_yamdb.git
```
В корне проекта скопируйте .env.template и назовите новый файл .env
```
cp .env.template .env
```
Заполните шаблон по этому примеру
```
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
Запустите проект
```
docker-compose up
```
Выполните первые миграции
```
docker exec -ti infra_sp2_web_1 python manage.py migrate
```
Создайте суперпользователя
```
docker exec -ti infra_sp2_web_1 python manage.py createsuperuser
```
При желании вы можете загрузить тестовый набор данных
```
docker exec -ti infra_sp2_web_1 python manage.py loaddata data.xml
```

Сайт доступен по адресу
```
http://localhost:8000/
```

## Использованные технологии

* [Python](https://www.python.org/) - Язык программирования
* [Django](https://www.djangoproject.com/) - Веб-фреймворк
* [PostgreSQL](https://www.postgresql.org/) - Реляционная база данных

## Авторы
* [Карина](https://github.com/Karina-karina)
* [Александр Соколов](https://github.com/Alvsok)
* [Шильцин Станислав](https://github.com/jlllk)

## Лицензия
Данный проект распростарняется под Лицензией MIT.