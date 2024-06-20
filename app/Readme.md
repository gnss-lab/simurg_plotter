# Чеклист
- [x] Изучение документации по Docker Compose, написание простого приложения на FastApi и запуск нескольких экземпляров
- [x] Тестирование использования Volume для контейнеров, запись файла в директорию и отключение контейнеров, проверка сохранения файла
- [x] Написание простого приложения для генерации рандомных графиков, проверка скачивания графиков из директории Volume, получение списка названий графиков из директории Volume
- [x] Использование simurg_plotter для построения одиночных графиков по заранее заданным опциональным аргументам и времени




# Commands
```cd /path/to/project```

```docker-compose up --build```

```docker-compose down```

Options: ```docker-compose up -d --build``` (start on background)


# Volume absolute path

```
services:
  app1:
    ...
    volumes:
      - /path/to/existing/data:/app/data  !!!
    ...

  app2:
    ...
    volumes:
      - /path/to/existing/data:/app/data  !!!
    ...

volumes:
  data:
```
