# Вызов всех необходимых библиотек
import json
import requests
import datetime
import sqlalchemy as sq
import prettytable as pt
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Класс для работы с базой данных
class Database:

    # Инициация значений для работы с базой данных
    def __init__(self, driver: str, username: str,
                 password: str, database: str,
                 server: str = 'localhost', port: str = '5432'):
        
        # Значения: драйвер, имя пользователя, пароль, имя базы данных, сервер, порт
        self.driver = driver
        self.username = username
        self.password = password
        self.database = database
        self.server = server
        self.port = port

    # Словарь классов, отвечающих за построение таблиц в базе данных
    CLASS_TABLE_DICT = {}

    # Запуск движка
    def get_engine(self):
        
        # Построение DSN
        DSN = f"{self.driver}://{self.username}:{self.password}@{self.server}:{self.port}/{self.database}"
        
        # Запуск и вывод движка
        engine = sq.create_engine(DSN)
        return engine

    # Создание таблиц
    def create_tables(self, engine):

        # Вызов базового класса
        Base = declarative_base()

        # Таблица publisher
        class Publisher(Base):
            __tablename__ = "publisher"
            id = sq.Column(sq.Integer, primary_key=True)
            name = sq.Column(sq.String(length=255), nullable=False, unique=True)
        
        # Таблица book
        class Book(Base):
            __tablename__ = "book"
            id = sq.Column(sq.Integer, primary_key=True)
            title = sq.Column(sq.String(length=255), nullable=False, unique=True)
            id_publisher = sq.Column(sq.Integer, sq.ForeignKey('publisher.id'), nullable=False)
            publisher = relationship("Publisher", backref="books")

        # Таблица shop
        class Shop(Base):
            __tablename__ = 'shop'
            id = sq.Column(sq.Integer, primary_key=True)
            name = sq.Column(sq.String(length=255), nullable=False, unique=True)
        
        # Таблица stock
        class Stock(Base):
            __tablename__ ='stock'
            id = sq.Column(sq.Integer, primary_key=True)
            id_book = sq.Column(sq.Integer, sq.ForeignKey('book.id'), nullable=False)
            id_shop = sq.Column(sq.Integer, sq.ForeignKey('shop.id'), nullable=False)
            count = sq.Column(sq.Integer, sq.CheckConstraint("stock.count>=0"), nullable=False)
            book = relationship("Book", backref="stocks")
            shop = relationship("Shop", backref="stocks")

        # Таблица sale
        class Sale(Base):
            __tablename__ ='sale'
            id = sq.Column(sq.Integer, primary_key=True)
            price = sq.Column(sq.DECIMAL(10, 2), sq.CheckConstraint("sale.price>0"), nullable=False)
            date_sale = sq.Column(sq.Date, nullable=False)
            id_stock = sq.Column(sq.Integer, sq.ForeignKey('stock.id'), nullable=False)
            count = sq.Column(sq.Integer, sq.CheckConstraint("sale.count>0"), nullable=False)
            stock = relationship("Stock", backref="sales")
        
        # Создание таблиц
        Base.metadata.create_all(engine)

        # Добавление классов, отвечающих за таблицы, в словарь CLASS_TABLE_DICT
        for class_name, my_class in zip(['publisher', 'book', 'shop', 'stock', 'sale'],
                                        [Publisher, Book, Shop, Stock, Sale]):
             self.CLASS_TABLE_DICT[class_name] = my_class

    # Извлечение json-файла по URL (для работы с данными из файла tests_data.json)
    def get_json_data(self, url: str) -> json:
        
        # Обращение к данным и вывод сведений из json-файла
        response = requests.request("GET", url)
        return response.json()

    # Корректировка дат
    def get_datetime(self, isoformat: str) -> datetime.datetime:

        # Использование библиотеки datetime для получения дат формата %Y-%m-%d
        date_time = datetime.datetime.strptime(isoformat,'%Y-%m-%dT%H:%M:%S.%f%z')
        return date_time.date()

    # Заполнение таблиц
    def fill_tables(self, engine, json_data: json):

        # Инициация сессии
        Session = sessionmaker(bind=engine)
        session = Session()

        # Подключение к классам
        for class_name, my_class in self.CLASS_TABLE_DICT.items():
            
            # Сбор данных для таблицы, принадлежащей к конкретному классу
            table_dict_data_list = [d.get('fields') for d in json_data if d.get('model') == class_name]

            # Корректировка даты в таблице sale, принадлежащей к классу Sale (столбец date_sale)
            if class_name == 'sale':
                for my_dict in table_dict_data_list:
                    my_dict['date_sale'] = self.get_datetime(my_dict.get('date_sale'))

            # Заполнение таблицы, принадлежащей к конкретному классу
            for my_dict in table_dict_data_list:
                model = my_class(**my_dict)
                session.add(model)

                # Фиксация изменений в базе данных
                session.commit()

        # Закрытие сессии
        session.close()

    # Получение информации о продаже книг конкретного издателя/автора
    def get_publisher_info(self, engine):

        # Создание сессии
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Получение классов
        class_name_list = ['publisher', 'book','stock','shop','sale']
        Publisher, Book, Stock, Shop, Sale = (self.CLASS_TABLE_DICT.get(n) for n in class_name_list)

        # Ввод параметров поиска
        print('Введите имя или идентификатор издателя (примеры ввода: O’Reilly, 1):')
        input_value = input()

        # Проверка типа вводимого значения
        try:
            int_try = int(input_value)
            condition = (Publisher.id == int_try)
        except ValueError:
            condition = (Publisher.name == input_value.strip())
        
        # Запрос на объединение таблиц с учетом интересующего издателя/автора
        query = session.query(Publisher, Book, Stock, Shop, Sale).\
                join(Book, Book.id_publisher == Publisher.id).\
                join(Stock, Stock.id_book == Book.id).\
                join(Shop, Stock.id_shop == Shop.id).\
                join(Sale, Sale.id_stock == Stock.id).\
                filter(condition)
        
        # Получение информации о продаже книг конкретного издателя/автора
        apps_iter_data = []
        for _, book, _, publisher, sale in query:
            apps_iter_data.append({'Название книги': book.title,
                                   'Название магазина': publisher.name,
                                   'Стоимость покупки': sale.price,
                                   'Дата покупки': sale.date_sale})

        # Вывод результата поиска в виде таблицы (библиотека prettytable)
        t = pt.PrettyTable([x for x in apps_iter_data[0].keys()])
        for i in apps_iter_data:
            row = list(i.values())
            t.add_row(row)
        print(t)

        # Фиксация изменений в базе данных
        session.commit()

        # Закрытие сессии
        session.close()

# Реализация всех написанных выше классов и методов
if __name__ == '__main__':

    # Вызов класса Database
    database = Database('postgresql', 'postgres', 'postgres', 'test')

    # Вызов движка
    engine = database.get_engine()

    # Создание таблиц в базе данных
    database.create_tables(engine)

    # Извлечение данных из файла tests_data.json
    json_data = database.get_json_data("https://raw.githubusercontent.com/netology-code/py-homeworks-db/SQLPY-76/06-orm/fixtures/tests_data.json")

    # Заполнение таблиц в базе данных
    database.fill_tables(engine, json_data)

    # Получение информации о продаже книг конкретного издателя/автора
    database.get_publisher_info(engine)
