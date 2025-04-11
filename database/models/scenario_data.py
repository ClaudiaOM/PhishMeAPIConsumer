from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid

class ScenarioData(Base):
    __tablename__ = 'ScenarioData'
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=str(uuid.uuid4()))
    Email = Column(String)
    Recipient_Name = Column(String)
    Recipient_Group = Column(String)
    Department = Column(String)
    Location = Column(String)
    Opened_Email = Column(Boolean)
    Opened_Email_Timestamp = Column(DateTime)
    Clicked_Link = Column(Boolean)
    Clicked_Link_Timestamp = Column(DateTime)
    Submitted_Form = Column(Boolean)
    Username = Column(String)
    Entered_Password = Column(String)
    Submitted_Form_Timestamp = Column(DateTime)
    Reported_Phish = Column(Boolean)
    New_Repeat_Reporter = Column(String)
    Reported_Phish_Timestamp = Column(DateTime)
    Time_to_Report_in_seconds = Column(Integer)
    Remote_IP = Column(String)
    GeoIP_Country = Column(String)
    GeoIP_City = Column(String)
    GeoIP_ISP = Column(String)
    Last_DSN = Column(String)
    Last_Email_Status = Column(String)
    Last_Email_Status_Timestamp = Column(DateTime)
    Language = Column(String)
    Browser = Column(String)
    User_Agent = Column(String)
    Mobile = Column(Boolean)
    Seconds_Spent_on_Education_Page = Column(Integer)
    Submitted_Data = Column(Boolean)
    UserType = Column(String)
    Address_Region = Column(String)
    Address2_Type = Column(String)
    Address_StreetAddress = Column(String)
    Title = Column(String)
    PhoneNumber3_Value = Column(String)
    PhoneNumber2_Value = Column(String)
    PhoneNumber4_Type = Column(String)
    PreferredLanguage = Column(String)
    Address2_Formatted = Column(String)
    PhoneNumber6_Value = Column(String)
    Address_Type = Column(String)
    NickName = Column(String)
    Address_Country = Column(String)
    PhoneNumber4_Value = Column(String)
    Address_Formatted = Column(String)
    PhoneNumber2_Type = Column(String)
    PhoneNumber3_Type = Column(String)
    Address_Locality = Column(String)
    Name_GivenName = Column(String)
    PhoneNumber_Type = Column(String)
    DisplayName = Column(String)
    PhoneNumber6_Type = Column(String)
    Manager_Value = Column(String)
    PhoneNumber5_Type = Column(String)
    Name_FamilyName = Column(String)
    Name_Formatted = Column(String)
    PhoneNumber_Value = Column(String)
    PhoneNumber5_Value = Column(String)
    Address_PostalCode = Column(String)
    Scenario_Id = Column(UNIQUEIDENTIFIER, ForeignKey('Scenario.Id'))
    Scenario = relationship('Scenario', backref='scenario_data')


    @staticmethod
    def from_json(data):
        return ScenarioData(
            Email = data.get('Email'),
            Recipient_Name = data.get('Recipient Name'),
            Recipient_Group = data.get('Recipient Group'),
            Department = data.get('Department'),
            Location = data.get('Location'),
            Opened_Email = data.get('Opened Email?') == 'Yes',
            Opened_Email_Timestamp = data.get('Opened Email Timestamp'),
            Clicked_Link = data.get('Clicked Link?') == 'Yes',
            Clicked_Link_Timestamp = data.get('Clicked Link Timestamp'),
            Submitted_Form = data.get('Submitted Form') == 'Yes',
            Username = data.get('Username') or data.get('userName'),
            Entered_Password = data.get('Entered Password?') == 'Yes',
            Submitted_Form_Timestamp = data.get('Submitted Form Timestamp'),
            Reported_Phish = data.get('Reported Phish?') == 'Yes',
            New_Repeat_Reporter = data.get('New/Repeat Reporter'),
            Reported_Phish_Timestamp = data.get('Reported Phish Timestamp'),
            Time_to_Report_in_seconds = data.get('Time to Report (in seconds)'),
            Remote_IP = data.get('Remote IP'),
            GeoIP_Country = data.get('GeoIP Country'),
            GeoIP_City = data.get('GeoIP City'),
            GeoIP_ISP = data.get('GeoIP ISP'),
            Last_DSN = data.get('Last DSN'),
            Last_Email_Status = data.get('Last Email Status'),
            Last_Email_Status_Timestamp = data.get('Last Email Status Timestamp'),
            Language = data.get('Language'),
            Browser = data.get('Browser'),
            User_Agent = data.get('User-Agent'),
            Mobile = data.get('Mobile?') == 'TRUE',
            Seconds_Spent_on_Education_Page = data.get('Seconds Spent on Education Page'),
            Submitted_Data = data.get('Submitted Data') == 'Yes',
            UserType = data.get('userType'),
            Address_Region = data.get('address_region'),
            Address2_Type = data.get('address2_type'),
            Address_StreetAddress = data.get('address_streetAddress'),
            Title = data.get('title'),
            PhoneNumber3_Value = data.get('phoneNumber3_value'),
            PhoneNumber2_Value = data.get('phoneNumber2_value'),
            PhoneNumber4_Type = data.get('phoneNumber4_type'),
            PreferredLanguage = data.get('preferredLanguage'),
            Address2_Formatted = data.get('address2_formatted'),
            PhoneNumber6_Value = data.get('phoneNumber6_value'),
            Address_Type = data.get('address_type'),
            NickName = data.get('nickName'),
            Address_Country = data.get('address_country'),
            PhoneNumber4_Value = data.get('phoneNumber4_value'),
            Address_Formatted = data.get('address_formatted'),
            PhoneNumber2_Type = data.get('phoneNumber2_type'),
            PhoneNumber3_Type = data.get('phoneNumber3_type'),
            Address_Locality = data.get('address_locality'),
            Name_GivenName = data.get('name_givenName'),
            PhoneNumber_Type = data.get('phoneNumber_type'),
            DisplayName = data.get('displayName'),
            PhoneNumber6_Type = data.get('phoneNumber6_type'),
            Manager_Value = data.get('manager_value'),
            PhoneNumber5_Type = data.get('phoneNumber5_type'),
            Name_FamilyName = data.get('name_familyName'),
            Name_Formatted = data.get('name_formatted'),
            PhoneNumber_Value = data.get('phoneNumber_value'),
            PhoneNumber5_Value = data.get('phoneNumber5_value'),
            Address_PostalCode = data.get('address_postalCode')
        )