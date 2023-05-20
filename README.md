
# T-Split

## Системные требования
* [Python 3.11](https://www.python.org/downloads/)
* [docker](https://docs.docker.com/get-docker/)
* [docker-compose](https://docs.docker.com/compose/install/)
* [Postman](https://www.postman.com/downloads/)

## Разработка
### Установка зависимостей
```shell
pip install -r requirements.txt
```
### Запуск приложения
```shell
docker-compose up -d db app
```
### Миграции
```shell
docker-compose exec -- app yoyo apply
```
### Тесты
```shell
docker-compose up tests
```

### Форматирование кода
```shell
docker-compose exec -- app black .
docker-compose exec -- app isort .
```

## Полезные ссылки

Введение в SQLAlchemy 2020 от автора https://youtu.be/1Va493SMTcY

Не использовать `async_scoped_session` https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#using-asyncio-scoped-session

Если используется alembic, необходимо дополнительно настоить метадату https://alembic.sqlalchemy.org/en/latest/naming.html

Подробно про asyncio в контексте БД: https://techspot.zzzeek.org/2015/02/15/asynchronous-python-and-databases/

Миграция на Mapped https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#migrating-an-existing-mapping

Челленджи SQLAlchemy 2.0 https://python-gino.org/docs/en/1.1b2/explanation/sa20.html

Мотивация для использования асинхронных ORM https://python-gino.org/docs/en/1.1b2/explanation/why.html

Транзакции для тестов https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites

Стили загрузок отношений https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#summary-of-relationship-loading-styles
