# Решение домашнего задания «Работа с PostgreSQL из Python»

[Домашнее задание](https://github.com/netology-code/py-homeworks-db/tree/SQLPY-76/06-orm) было решено с использованием Python 3.9. Файл с кодом (homework.py) и требования для его выполнения (requirements.txt) приложены в текущем репозитории.


## Структура кода

Код, содержащийся в <code>.py </code> файле, состоит из следующих частей:

1. Вызов следующих библиотек: json, requests, datetime, sqlalchemy, prettytable.
2. Формирование методов класса <code>Database</code> (работа с базой данных):
   * формирование вводных параметов класса: драйвер, имя пользователя, пароль, имя базы данных, сервер (по умолчанию <code>localhost</code>), порт (по умолчанию <code>5432</code>);
   * метод <code>get_engine</code>: запуск и вывод движка, необходимого для созадния таблиц и инициации сессий;
   * метод <code>create_tables</code>: вызов базового класса и создание таблиц;
   * метод <code>get_json_data</code>: извлечение файла tests_data.json по [URL](https://raw.githubusercontent.com/netology-code/py-homeworks-db/SQLPY-76/06-orm/fixtures/tests_data.json);
   * метод <code>get_datetime</code>: корректировка дат файла tests_data.json;
   * метод <code>fill_tables</code>: инициация сессии для заполнения таблиц, созданных в рамках метода <code>create_tables</code>;
   * метод <code>get_publisher_info</code>: инициация сессии для получения информации о продаже книг конкретного издателя/автора.
3. Реализация:
   * вызов класса <code>Database</code>;
   * вызов движка;
   * создание таблиц в базе данных;
   * извлечение данных из файла tests_data.json по [URL](https://raw.githubusercontent.com/netology-code/py-homeworks-db/SQLPY-76/06-orm/fixtures/tests_data.json);
   * заполнение таблиц в базе данных;
   * получение информации о продаже книг конкретного издателя/автора.