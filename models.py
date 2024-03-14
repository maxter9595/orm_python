# Импортирование сторонних библиотек
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

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
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey("publisher.id"), nullable=False)
    publisher = relationship("Publisher", backref="books")


# Таблица shop
class Shop(Base):
    __tablename__ = "shop"
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=255), nullable=False, unique=True)


# Таблица stock
class Stock(Base):
    __tablename__ = "stock"
    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey("book.id"), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey("shop.id"), nullable=False)
    count = sq.Column(sq.Integer, sq.CheckConstraint("stock.count>=0"), nullable=False)
    book = relationship("Book", backref="stocks")
    shop = relationship("Shop", backref="stocks")


# Таблица sale
class Sale(Base):
    __tablename__ = "sale"
    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(
        sq.DECIMAL(10, 2), sq.CheckConstraint("sale.price>0"), nullable=False
    )
    date_sale = sq.Column(sq.Date, nullable=False)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey("stock.id"), nullable=False)
    count = sq.Column(sq.Integer, sq.CheckConstraint("sale.count>0"), nullable=False)
    stock = relationship("Stock", backref="sales")


def create_tables(engine):
    # Создание таблиц
    Base.metadata.create_all(engine)
