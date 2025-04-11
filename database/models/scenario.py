from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid

class Scenario(Base):
    __tablename__ = 'Scenario'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=str(uuid.uuid4()))
    SimpleId = Column(Integer)
    Title = Column(String)
    Description = Column(String)
    Scenario_Type = Column(String)
    Email_Subject = Column(String)
    Date_Started = Column(DateTime)
    Date_Finished = Column(DateTime)
    Recipients = Column(String)
    Full_CSV_Url = Column(String)
    Notes = Column(String)
    Is_Archive = Column(Boolean)
    Status = Column(String)
    Activity_Timeline_Url = Column(String)
    Company_Id = Column(UNIQUEIDENTIFIER, ForeignKey('Company.Id'))
    Company = relationship('Company', backref='scenarios')
    Fully_Downloaded = Column(Boolean)

    @staticmethod
    def from_json(data):
        return Scenario(
            Id=data.get('id'),
            SimpleId=data.get('simple_id'),
            Title=data.get('title'),
            Description=data.get('description'),
            Scenario_Type=data.get('scenario_type'),
            Email_Subject=data.get('email_subject'),
            Date_Started=datetime.strptime(data.get('date_started'), "%Y-%m-%dT%H:%M:%SZ") if data.get('date_started') else None,
            Date_Finished=datetime.strptime(data.get('date_finished'), "%Y-%m-%dT%H:%M:%SZ") if data.get('date_finished') else None,
            Recipients=data.get('recipients'),
            Full_CSV_Url=data.get('full_csv_url'),
            Notes=data.get('notes'),
            Is_Archive=data.get('is_archive'),
            Status=data.get('status'),
            Activity_Timeline_Url=data.get('activity_timeline_url'),
        )
    

