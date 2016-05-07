from sqlalchemy import Column, String, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Weights(Base):
    __tablename__ = 'weights'
    id = Column(Integer, primary_key=True, nullable=False)
    user = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    weight = Column(Float, nullable=False)


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, nullable=False)
    comment = Column(String, nullable=False)
    date = Column(Date, nullable=False)


class Users(Base):
    __tablename__ = 'users'
    user = Column(String, primary_key=True, nullable=False)
    max_allowed_weight = Column(Integer, nullable=False)
    goal = Column(Integer, nullable=False)
    next_goal = Column(Integer, nullable=False)