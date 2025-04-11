from sqlalchemy import Column, Integer, String, DateTime
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid


class Client(Base):
    __tablename__ = 'Client'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=str(uuid.uuid4()))
    Name = Column(String)
