import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base();

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(), nullable=False)
    picture = Column(String())

class Category(Base):
    """docstring fs Category."""
    __tablename__ = 'category'

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'category': self.name,
            'id'      : self.id,
            'user_id' : self.user_id
        }

class Product(Base):
    """docstring fs Product."""
    __tablename__ = 'product'

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    description = Column(String())
    price = Column(String())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

# Adding this serialize function to be able to send JSON objects in a
# serializable format

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id' : self.user_id,
            'description': self.description,
            'price': self.price
        }


engine = create_engine('sqlite:///Amazonwithusers.db');
Base.metadata.create_all(engine);

print('Database created sucessfully!!!');
