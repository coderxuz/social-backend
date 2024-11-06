from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base, engine
from enum import Enum as PyEnum
from datetime import datetime

#Like class
class Like (Base):
    __tablename__ = 'likes'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    
    user = relationship('User', back_populates='liked_posts')
    post = relationship('Post', back_populates='likers')

#Comment class    
class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments') 

#User class
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    user_img = Column(Integer)
    
    post = relationship("Post", back_populates='user')
    liked_posts = relationship('Like', back_populates='user')
    comments = relationship("Comment", back_populates='user')

#Image class    
class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String)
    
    post = relationship('Post', back_populates='image')
    
#Post class
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    image_id = Column(Integer, ForeignKey('image.id'),nullable=True)
    
    user = relationship("User", back_populates='post')
    image = relationship('Image', back_populates='post')
    likers = relationship('Like', back_populates='post')
    comments = relationship("Comment", back_populates='post')
if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)