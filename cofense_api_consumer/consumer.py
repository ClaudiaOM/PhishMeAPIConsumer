import requests
from .custom_exceptions import RateLimitError

class APIConsumer:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.header = {'Authorization': f'Token token={self.token}'}

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        header = self.header
        response = requests.get(url, headers=header,  params=params)
        response.raise_for_status()
        return response.json()
    
    def get_csv(self, endpoint, params=None):
        response = requests.get(f"{self.base_url}/{endpoint}", headers=self.header,  params=params)
        if response.text.startswith("API Token Busy"):
            raise RateLimitError(response.text)
        else:
            response.raise_for_status()
        if response.headers['Content-Type'] != 'text/csv':
            raise ValueError("URL did not return a csv")
        return response.text
    
    def get_csv_url(self, url, params=None):
        response = requests.get(url, headers=self.header,  params=params)
        if response.text.startswith("API Token Busy"):
            raise RateLimitError(response.text)
        else:
            response.raise_for_status()
        if response.headers['Content-Type'] != 'text/csv':
            raise ValueError("URL did not return a csv")
        return response.text
    