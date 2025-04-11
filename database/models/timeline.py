from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid

class Timeline(Base):
    __tablename__ = 'Timeline'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=str(uuid.uuid4()))
    Timestamp = Column(DateTime)
    Action = Column(String)
    Tracking_ID = Column(String)
    Recipient = Column(String)
    Group = Column(String)
    Remote_IP = Column(String)
    Form_Username = Column(String)
    Form_Password = Column(String)
    Country = Column(String)
    City = Column(String)
    ISP = Column(String)
    Browser = Column(String)
    User_Agent_String = Column(String)
    Mobile = Column(Boolean)
    Email_Client = Column(String)
    In_User_Agents_Charts = Column(Boolean)
    Scenario_Id = Column(UNIQUEIDENTIFIER, ForeignKey('Scenario.Id'))
    Scenario = relationship('Scenario', backref='timeline')


    @staticmethod
    def from_json(data):
        return Timeline(
            Timestamp = data.get('Timestamp'),
            Action = data.get('Action'),
            Tracking_ID = data.get('Tracking ID'),
            Recipient = data.get('Recipient'),
            Group = data.get('Group'),
            Remote_IP = data.get('Remote IP'),
            Form_Username = data.get('Form Username'),
            Form_Password = data.get('Form Password'),
            Country = data.get('Country'),
            City = data.get('City'),
            ISP = data.get('ISP'),
            Browser = data.get('Browser'),
            User_Agent_String = data.get('User-Agent String'),
            Mobile = data.get('Mobile?') == '1',
            Email_Client = data.get('Email Client?') ,
            In_User_Agents_Charts = data.get('In User Agents charts?') == '1'
        )