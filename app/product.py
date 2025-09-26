class Product:
    def __init__(self, product_id, product_name, product_description, product_quantity, product_price, supplier_ids=None, category_ids=None, image_ids=None):
        self.product_id = product_id
        self.product_name = product_name
        self.product_description = product_description
        self.product_quantity = product_quantity
        self.product_price = product_price
        self.supplier_ids = supplier_ids or []
        self.category_ids = category_ids or []
        self.image_ids = image_ids or []

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
    
    def add_supplier(self, supplier_id):
        self.supplier_ids.append(supplier_id)
    
    def remove_supplier(self, supplier_id):
        self.supplier_ids.remove(supplier_id)

    def add_category(self, category_id):
        self.category_ids.append(category_id)

    def remove_category(self, category_id):
        self.category_ids.remove(category_id)

    def add_image(self, image_id):
        self.image_ids.append(image_id)

    def remove_image(self, image_id):
        self.image_ids.remove(image_id)

    