class Category:
    def __init__(self, category_id, category_name, category_description, product_ids=None):
        self.category_id = category_id
        self.category_name = category_name
        self.category_description = category_description
        self.product_ids = product_ids or []

        def add_product(self, product_id):
            self.product_ids.append(product_id)

        def remove_product(self, product_id):
            self.product_ids.remove(product_id)