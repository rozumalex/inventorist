from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    created = Column(Integer)

    def __init__(self, id, first_name, last_name, created):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.created = created


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    created = Column(Integer)
    name = Column(String)
    memory = Column(String)

    def __init__(self, id, created, name):
        self.id = id
        self.created = created
        self.name = name


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    chat = Column(Integer)
    name = Column(String)

    __table_args__ = (UniqueConstraint('chat', 'name', name='_chat_name_uni'),)

    def __init__(self, chat, name):
        self.chat = chat
        self.name = name


class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    chat = Column(Integer)
    category = Column(String)
    name = Column(String)

    def __init__(self, chat, category, name):
        self.chat = chat
        self.category = category
        self.name = name


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    chat = Column(Integer, ForeignKey(Chat.id))
    user = Column(Integer, ForeignKey(User.id))
    category = Column(String)
    position = Column(String)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    time = Column(Integer)
    value = Column(Float)

    def __init__(self, chat, user, category, position, year, month, day, time,
                 value):
        self.chat = chat
        self.user = user
        self.category = category
        self.position = position
        self.year = year
        self.month = month
        self.day = day
        self.time = time
        self.value = value
