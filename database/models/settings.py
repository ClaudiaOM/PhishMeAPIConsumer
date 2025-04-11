from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from .base import Base

class Settings(Base):
    __tablename__ = 'Settings'
    
    Id = Column(Integer, primary_key=True)
    Key = Column(String)
    Value = Column(String)
