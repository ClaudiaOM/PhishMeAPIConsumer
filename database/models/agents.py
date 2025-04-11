from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class HuntressAgents(Base):
    __tablename__ = 'HuntressAgent'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid.uuid4()))
    Agent_Id = Column(Integer)
    Version = Column(String)    
    Arch = Column(String)    
    Win_Build_Number = Column(Integer)
    Domain_Name = Column(String)    
    Created_At = Column(DateTime)
    Hostname = Column(String)    
    Ipv4_Address = Column(String)    
    External_Ip = Column(String)    
    Updated_At = Column(DateTime)
    Last_Survey_At = Column(DateTime)
    Last_Callback_At = Column(DateTime)
    Account_Id = Column(Integer)    
    Platform = Column(String)      
    Os = Column(String)      
    Service_Pack_Major = Column(Integer)    
    Service_Pack_Minor = Column(Integer)    
    Os_Major = Column(Integer)    
    Os_Minor = Column(Integer)    
    Os_Patch = Column(Integer)     
    Version_Number = Column(Integer)   
    Edr_Version = Column(String)      
    Os_Build_Version = Column(String)      
    Serial_Number = Column(String)      
    Organization_Id = Column(UNIQUEIDENTIFIER, ForeignKey('HuntressOrganization.Id'))
    organization = relationship('HuntressOrganization', backref='agents')
    

    from datetime import datetime

    def from_dict(self, data):
        self.Agent_Id = data['id']
        self.Version = data['version']
        self.Arch = data['arch']
        self.Win_Build_Number = data['win_build_number']
        self.Domain_Name = data['domain_name']
        self.Created_At = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%SZ') if 'created_at' in data else None
        self.Hostname = data['hostname']
        self.Ipv4_Address = data['ipv4_address']
        self.External_Ip = data['external_ip']
        self.Updated_At = datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%SZ') if 'updated_at' in data else None
        self.Last_Survey_At = datetime.strptime(data['last_survey_at'], '%Y-%m-%dT%H:%M:%SZ') if 'last_survey_at' in data and data['last_survey_at'] is not None else None
        self.Last_Callback_At = datetime.strptime(data['last_callback_at'], '%Y-%m-%dT%H:%M:%SZ') if 'last_callback_at' in data else None
        self.Account_Id = data['account_id']
        self.Platform = data['platform']
        self.Os = data['os']
        self.Service_Pack_Major = data['service_pack_major']
        self.Service_Pack_Minor = data['service_pack_minor']
        self.Os_Major = data['os_major']
        self.Os_Minor = data['os_minor']
        self.Os_Patch = data['os_patch']
        self.Version_Number = data['version_number']
        self.Edr_Version = data['edr_version']
        self.Os_Build_Version = data['os_build_version']
        self.Serial_Number = data['serial_number']

        return self