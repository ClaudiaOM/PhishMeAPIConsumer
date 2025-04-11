class ParamBuilder:
    def __init__(self):
        self.params = {}

    def started_before(self, date):
        self.params['filter[started_before]'] = date
        return self
    
    def started_after(self, date):
        self.params['filter[started_after]'] = date
        return self
    
    def page(self, page):
        self.params['page'] = page
        return self
    
    def per_page(self, per_page):
        self.params['per_page'] = per_page
        return self
    
    def build(self):
        return self.params