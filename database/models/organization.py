from .base import Base

import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship

class HuntressOrganization(Base):
    __tablename__ = 'HuntressOrganization'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid.uuid4()))
    Organization_Id = Column(Integer)    
    Name = Column(String)    
    Created_At = Column(DateTime)
    Updated_At = Column(DateTime)
    Account_Id = Column(Integer)
    Agents_Count = Column(Integer)
    Incident_Reports_Count = Column(Integer)
    Microsoft_365_Users_Count = Column(Integer)
    Key = Column(String)
    Last_Download = Column(DateTime, default=datetime(2010, 1, 2))
    Client_Id = Column(UNIQUEIDENTIFIER, ForeignKey('Client.Id'))
    client = relationship('Client', backref='organizations')


    def from_dict(self, data):
        self.Organization_Id = data['id']
        self.Name = data['name']
        self.Created_At = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        self.Updated_At = datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        self.Account_Id = data['account_id']
        self.Agents_Count = data['agents_count']
        self.Incident_Reports_Count = data['incident_reports_count']
        self.Microsoft_365_Users_Count = data['microsoft_365_users_count']
        self.Key = data['key']
        return self
