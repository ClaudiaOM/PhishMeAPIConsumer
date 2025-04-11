from typing import Type
from sqlalchemy.orm import Session
from ..models.settings import Settings
from .base_repository import BaseRepository

class SettingsRepository(BaseRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Settings)

    def get_last_run(self):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'LastRun').first()
        return setting.Value if setting else None
        
    def get_cofense_api_url(self):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'ApiUrl').first()
        return setting.Value if setting else None
    
    def get_last_group(self):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'LastGroup').first()
        return setting.Value if setting else None
    
    def update_last_run(self, value):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'LastRun').first()
        setting.Value = value
        self.save_entity(setting)
        
    def update_last_group(self, value):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'LastGroup').first()
        setting.Value = value
        self.save_entity(setting)
        
    def get_huntress_api_url(self):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'HuntressAPI').first()
        return setting.Value if setting else None

    def get_batch_size(self):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'BatchSize').first()
        return int(setting.Value) if setting else None
    
    def get_token(self):
        setting = self.session.query(self.entity_class).filter(self.entity_class.Key == 'HuntressKey').first()
        return setting.Value if setting else None
    