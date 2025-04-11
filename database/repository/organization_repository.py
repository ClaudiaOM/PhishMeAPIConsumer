

from .base_repository import BaseRepository
from ..models.organization import HuntressOrganization
from datetime import datetime

class Organization_Repository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, HuntressOrganization)
        self.repository = self

    def get_organizations(self):
        return self.repository.get()
    
    def get_organizations_by_client(self, client_id):
        return self.repository.search_by_property(Client_Id = client_id)
    
    def get_organizations_by_id(self, organization_id):
        return self.repository.search_by_property(Organization_Id = organization_id)
    
    def get_batch(self, batch_size: int):
        companies = self.repository.get()

        companies.sort(key=lambda x: x.Last_Download)

        return companies[:batch_size]
    
    def update_last_download(self, organization: HuntressOrganization):
        organization.Last_Download = datetime.now()
        self.repository.update(organization)

    
