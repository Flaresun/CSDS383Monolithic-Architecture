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