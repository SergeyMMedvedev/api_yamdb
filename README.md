# api_yamdb

Проект представляет собой API сервиса отзывов о фильмах, книгах и музыке
Зарегистрированные пользователи могут оставлять отзывы (Review) на произведения (Title).
Произведения делятся на категории (Category): «Книги», «Фильмы», «Музыка». 
Список категорий может быть расширен администратором. 

## Начало

Клонировать проект:
```
Git clone https://github.com/SergeyMMedvedev/api_yamdb.git
```

### Установка

Перейти в корневую директорию проекта и активировать виртуальное окружение 
```
$ source venv/Scripts/activate
```

Установить requirements

```
$ pip install requirements.txt
```

Запуск сервера разработчика
 
```
$ python manage.py runserver
```

## Проверка работоспособности

Примеры запросов к api_yamdb:

GET http://127.0.0.1:8000/api/v1/titles/

Response:
```
{
    "count": 10,
    "next": "http://localhost:8000/api/v1/titles/?page=2",
    "previous": null,
    "results": [
        {
            "id": 29,
            "name": "Elvis Presley - Blue Suede Shoes",
            "year": 1955,
            "rating": null,
            "description": "1",
            "genre": [],
            "category": {
                "name": "Музыка",
                "slug": "music"
            }
        },
        ...
    ]
}
```
GET
http://localhost:8000/api/v1/titles/1/reviews/


```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 151,
            "author": "admin5",
            "title": {
                "id": 1,
                "name": "Побег из Шоушенка",
                "year": 1994,
                "rating": 10,
                "description": "1",
                "genre": [],
                "category": {
                    "name": "Фильм",
                    "slug": "movie"
                }
            },
            "score": 10,
            "text": "Отзыв на Побег из Шошенка",
            "pub_date": "2021-01-26T15:21:00.499958Z"
        }
    ]
}
```
Полный список доступных запросов к приложению можно посмотреть:
* http://127.0.0.1:8000/redoc/

Для изменения содержания базы данных монжо воспользоваться админкой Django:
* http://127.0.0.1:8000/admin/


## Автор

* **Сергей Медведев** -  [SergeyMMedvedev](https://github.com/SergeyMMedvedev)
