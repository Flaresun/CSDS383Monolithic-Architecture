class Supplier:
    def __init__(self, supplier_id, supplier_name, supplier_contact, product_ids=None):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.supplier_contact = supplier_contact
        self.product_ids = product_ids or []

        def add_product(self, product_id):
            self.product_ids.append(product_id)

        def remove_product(self, product_id):
            self.product_ids.remove(product_id)    