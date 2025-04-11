from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
import uuid


class HuntressIncident(Base):
    __tablename__ = 'HuntressIncident'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid.uuid4()))
    Incident_Id = Column(Integer)
    Status = Column(String)    
    Summary = Column(String)    
    Body = Column(String)    
    Updated_At = Column(DateTime)
    Agent_Id = Column(Integer)
    Platform = Column(String)      
    Status_Updated_At = Column(DateTime)
    Organization_Id = Column(Integer)
    Sent_At = Column(DateTime)    
    Account_Id = Column(Integer)    
    Created_By_Id = Column(Integer)    
    Remediation_Instructions = Column(String)    
    Footholds = Column(String)    
    Severity = Column(String)    
    Assigned_To_Id = Column(Integer)    
    Closed_At = Column(DateTime)
    Last_Callback_At = Column(DateTime)
    Os = Column(String)      
    Os_Major = Column(Integer)    
    Os_Minor = Column(Integer)    
    Os_Patch = Column(Integer)     
    Version_Number = Column(Integer)   
    Edr_Version = Column(String)      
    Os_Build_Version = Column(String)      
    Serial_Number = Column(String)      
    Huntress_Organization_Id = Column(UNIQUEIDENTIFIER, ForeignKey('HuntressOrganization.Id'))
    organization = relationship('HuntressOrganization', backref='incidents')
    
    def from_dict(self, data):
        self.Incident_Id = data['id']
        self.Status = data['status'] if 'status' in data else None
        self.Summary = data['summary'] if 'summary' in data else None
        self.Body = data['body'] if 'body' in data else None 
        self.Updated_At = data['updated_at'] if 'updated_at' in data else None
        self.Agent_Id = data['agent_id'] if 'agent_id' in data else None
        self.Platform = data['platform'] if 'platform' in data else None
        self.Status_Updated_At = data['status_updated_at'] if 'status_updated_at' in data else None
        self.Sent_At = data['sent_at'] if 'sent_at' in data else None
        self.Account_Id = data['account_id'] if 'account_id' in data else None
        self.Created_By_Id = data['created_by_id'] if 'created_by_id' in data else None
        self.Remediation_Instructions = data['remediation_instructions'] if 'remediation_instructions' in data else None
        self.Footholds = data['footholds'] if 'footholds' in data else None
        self.Severity = data['severity'] if 'severity' in data else None
        self.Assigned_To_Id = data['assigned_to_id'] if 'assigned_to_id' in data else None
        self.Closed_At = data['closed_at'] if 'closed_at' in data else None
        self.Last_Callback_At = data['last_callback_at'] if 'last_callback_at' in data else None
        self.Os = data['os'] if 'os' in data else None
        self.Os_Major = data['os_major'] if 'os_major' in data else None
        self.Os_Minor = data['os_minor'] if 'os_minor' in data else None
        self.Os_Patch = data['os_patch'] if 'os_patch' in data else None
        self.Version_Number = data['version_number'] if 'version_number' in data else None
        self.Edr_Version = data['edr_version'] if 'edr_version' in data else None
        self.Os_Build_Version = data['os_build_version'] if 'os_build_version' in data else None
        self.Serial_Number = data['serial_number'] if 'serial_number' in data else None
        self.Organization_Id = data['organization_id'] if 'organization_id' in data else None
        return self
