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

class Follows(Base):
    __tablename__ = 'follows'
    follower_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    followed_user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

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

# Chat class
class Chat(Base):
    __tablename__ = 'chat'
    
    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    sender = relationship('User', foreign_keys=[sender_id])
    receiver = relationship('User', foreign_keys=[receiver_id])

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
    
    following = relationship(
        "User",
        secondary='follows',
        primaryjoin=id == Follows.follower_id,
        secondaryjoin=id == Follows.followed_user_id,
        backref='followers'
    )
    def __repr__(self):
        return f"{self.username}"
    @property
    def follower_count(self):
        return len(self.followers)
    @property
    def followings_count(self):
        return len(self.following)
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
# user1 = User(
#     first_name = 'John',
#     email = 'john@gmail.com',
#     password = 'john',
#     username = 'john',
# )
# user2 = User(
#     first_name = 'John2',
#     email = 'john2@gmail.com',
#     password = 'john2',
#     username = 'john2',
# )
# user1.following.append(user2)

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)