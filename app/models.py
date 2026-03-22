from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)

    shanyraks = relationship("Shanyrak", back_populates="owner", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")


class Shanyrak(Base):
    __tablename__ = "shanyraks"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    area = Column(Float, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="shanyraks")
    comments = relationship("Comment", back_populates="shanyrak", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shanyrak_id = Column(Integer, ForeignKey("shanyraks.id"), nullable=False)

    author = relationship("User", back_populates="comments")
    shanyrak = relationship("Shanyrak", back_populates="comments")