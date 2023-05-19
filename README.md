
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
