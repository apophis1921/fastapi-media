from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column , String , Text , DateTime ,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession , create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase , relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase , SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID,Base):
    '''Defining posts in user model'''
    posts = relationship("Post", back_populates="user") #this means - A user has many posts.

    #'''means a string literal but when not assigned a value->not passed for execution(runtime_)->used as comments
    #back_populates meaning
    '''back_populates="user"   # points to Post.user       
       back_populates="posts"  # points to User.posts'''

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)#primary key of posts database table
    user_id=Column(UUID(as_uuid=True),ForeignKey("user.id"),nullable=False)
    caption = Column(Text)
    url=Column(String,nullable=False)
    file_name=Column(String,nullable=False)
    file_type=Column(String,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)

    '''Defining user in post model'''
    user= relationship("User", back_populates="posts") #This means:"Every post belongs to one user."
    '''user.posts  ->    # Get all posts of a user
       post.user   ->    # Get the owner of a post'''


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine,expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session()-> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session 
                
async def get_user_db(session : AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)