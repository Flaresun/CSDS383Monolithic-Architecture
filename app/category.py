import re 
class Category:
    def __init__(self, category_id, category_name, category_description, product_ids=None):
        self.category_id = category_id
        self.category_name = category_name
        self.category_description = category_description
        self.product_ids = product_ids or []

    def isUUID(self,id):
        UUID_Check = re.compile(
            r'^[0-9a-fA-F]{8}-'
            r'[0-9a-fA-F]{4}-'
            r'[1-5][0-9a-fA-F]{3}-'
            r'[89ABab][0-9a-fA-F]{3}-'
            r'[0-9a-fA-F]{12}$'
        )
        return bool(UUID_Check.fullmatch(id))
    
    def set_category_id(self,id):
        # Id must be a UUID
        if not self.isUUID(id):
            print("ID must be a UUID")
            return 
        self.category_id = id

    def set_category_name(self,name):
        self.category_name = name
    def set_category_description(self,desc):
        self.category_description=desc

    def get_category_name(self):
        return self.category_name
    def get_category_description(self):
        return self.category_description
    def get_category_id(self):
        return self.category_id
    

    def add_product(self, product_id):
        self.product_ids.append(product_id)

    def remove_product(self, product_id):
        self.product_ids.remove(product_id)
    
    def __str__(self):
        return f"Category: Id='{self.category_id}', Name='{self.category_name}', Description='{self.category_description}', ProductIds='{self.product_ids}' "