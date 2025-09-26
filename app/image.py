import re 
class Image:
    def __init__(self, image_id, product_id, image_url):
        self.image_id = image_id
        self.product_id = product_id
        self.image_url = image_url
    
    def isUUID(self,id):
        UUID_Check = re.compile(
            r'^[0-9a-fA-F]{8}-'
            r'[0-9a-fA-F]{4}-'
            r'[1-5][0-9a-fA-F]{3}-'
            r'[89ABab][0-9a-fA-F]{3}-'
            r'[0-9a-fA-F]{12}$'
        )
        return bool(UUID_Check.fullmatch(id))
    
    def set_image_id(self,id):
        # Id must be a UUID
        if not self.isUUID(id):
            print("ID must be a UUID")
            return 
        self.image_id = id

    def get_image_id(self):
        return self.image_id

    def set_product_id(self,id):
        if not self.isUUID(id):
            print("ID must be a UUID")
            return
        self.product_id =id
    def get_product_id(self):
        return self.product_id

    def set_image_url(self,url):
        self.image_url = url
    def get_image_url(self):
        return self.image_url
    
    def __str__(self):
            return f"Image: Id='{self.image_id}', Product Id='{self.product_id}', Url='{self.image_url}', "