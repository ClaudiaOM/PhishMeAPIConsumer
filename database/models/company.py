from sqlalchemy import Column, Integer, String, DateTime
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid


class Company(Base):
    __tablename__ = 'Company'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=str(uuid.uuid4()))
    Name = Column(String)
    GroupName = Column(String)
    API = Column(String)
    Date_Added = Column(DateTime)

