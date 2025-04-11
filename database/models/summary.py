from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
import uuid


class HuntressSummary(Base):
    __tablename__ = 'HuntressSummary'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid.uuid4()))
    Summary_Id = Column(Integer)    
    Period = Column(String)       
    Created_At = Column(DateTime)
    Updated_At = Column(DateTime)
    Url = Column(String)
    Huntress_Organization_Id = Column(UNIQUEIDENTIFIER, ForeignKey('HuntressOrganization.Id'))
    organization = relationship('HuntressOrganization', backref='summary')

    def from_dict(self, data):
        self.Summary_Id = data['id']
        self.Period = data['period'] if 'period' in data else None
        self.Created_At = data['created_at'] if 'created_at' in data else None
        self.Updated_At = data['updated_at'] if 'updated_at' in data else None
        self.Url = data['url'] if 'url' in data else None
        self.Huntress_Organization_Id = data['organization_id'] if 'organization_id' in data else None
        return self
