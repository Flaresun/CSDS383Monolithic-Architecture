import uuid 
import sqlite3
import product
import image
import supplier
import category
from supplier import (
    create_supplier, read_supplier, update_supplier,
    delete_supplier, add_product_to_supplier, remove_product_from_supplier
)
conn = sqlite3.connect(":memory:")
cur = conn.cursor()

## Create Product table
cur.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        Product_Id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        Product_Name TEXT NOT NULL,
        Product_Description TEXT,
        Product_Quantity INTEGER NOT NULL CHECK (Product_Quantity >= 0),
        Product_Price REAL NOT NULL CHECK (Product_Price > 0),
        Supplier_Ids TEXT DEFAULT '[]',   -- store JSON array
        Category_Ids TEXT DEFAULT '[]',
        Image_Ids TEXT DEFAULT '[]'
    )
""")


## Create Supplier table 
cur.execute("""
    CREATE TABLE IF NOT EXISTS Suppliers (
        Supplier_Id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        Supplier_Name TEXT NOT NULL,
        Supplier_Contact TEXT NOT NULL,
        Product_Ids TEXT DEFAULT '[]'  -- store JSON array of UUIDs
    )
""")


## Create Category data 
cur.execute("""
    CREATE TABLE IF NOT EXISTS Category (
        Category_Id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        Category_Name TEXT NOT NULL,
        Category_Description TEXT,
        Product_Ids TEXT  -- you can store JSON array of UUIDs here
    )
""")

## Create Image data 
cur.execute("""
    CREATE TABLE IF NOT EXISTS Images (
        Image_Id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        Product_Id TEXT NOT NULL,
        Image_URL TEXT NOT NULL
    )
""")

# CLI Loop
if __name__ == "__main__":
    print("\n************************************ CLI RUNNING ************************************\n")
    while True:
        class_to_create  = str(input("What would you like to add? (Product, Image, Supplier, or Category): "))
        class_to_create = class_to_create.replace(" ", "").lower()
        
        if class_to_create == "product":
            command = input("Product Class: Create, Read, Update, Delete: ")

            try:
                if command == "Create":
                    name = input("Product Name: ").strip()
                    desc = input("Product Description: ").strip()
                    quantity = int(input("Product Quantity (integer >=0): ").strip())
                    price = float(input("Product Price (float >0): ").strip())

                    if quantity < 0:
                        print("Quantity must be >= 0")
                        continue
                    if price <= 0:
                        print("Price must be > 0")
                        continue
                    
                    product_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO Products (Product_Id, Product_Name, Product_Description, Product_Quantity, Product_Price, Supplier_Ids, Category_Ids, Image_Ids)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (product_id, name, desc, quantity, price, "[]", "[]", "[]"))
                    conn.commit()
                    print(f"Created Product with ID: {product_id}")
                elif command == "Read":
                    product_id = input("Product Id (UUID): ").strip()
                    if product_id:
                        cur.execute("SELECT * FROM Products WHERE Product_Id = ?", (product_id,))
                        output = cur.fetchone()
                        if output:
                            print({
                                "product_id": output[0],
                                "product_name": output[1],
                                "product_description": output[2],
                                "product_quantity": output[3],
                                "product_price": output[4],
                                "supplier_ids": output[5],
                                "category_ids": output[6],
                                "image_ids": output[7],
                            })
                        else:
                            print("Product Id not found")
                elif command == "Update":
                    product_id = input("Product Id (UUID): ").strip()

                    cur.execute("SELECT * FROM Products WHERE Product_Id = ?", (product_id,))
                    if not cur.fetchone():
                        print("Product Id does not exist")
                        continue
                    
                    name = input("New Product Name (leave blank if no change): ").strip()
                    desc = input("New Product Description (leave blank if no change): ").strip()
                    quantity = input("New Product Quantity (leave blank if no change): ").strip()
                    price = input("New Product Price (leaeve blank if no change): ").strip()

                    updates = []
                    values = []

                    if name:
                        updates.append("Product_Name = ?")
                        values.append(name)

                    if desc:
                        updates.append("Product_Description = ?")
                        values.append(desc)
                    
                    if quantity:
                        try:
                            quantity = int(quantity)
                            if quantity < 0:
                                print("Quantity must be >= 0")
                                continue
                            updates.append("Product_Quantity = ?")
                            values.append(quantity)
                        except ValueError:
                            print("Quantity must be an integer")
                            continue

                    if  price:
                        try:
                            price = float(price)
                            if price <= 0:
                                print("Price must be > 0")
                                continue
                            updates.append("Product_Price = ?")
                            values.append(price)
                        except ValueError:
                            print("Price must be a float")
                            continue
                        
                    if updates:
                        values.append(product_id)
                        sql = f"UPDATE Products SET {', '.join(updates)} WHERE Product_Id = ?"
                        cur.execute(sql, tuple(values))
                        conn.commit()
                        print("Product updated")
                    else:
                        print("No updates provided")
                elif command == "Delete":
                    product_id = input("Product Id (UUID): ").strip()
                    cur.execute("SELECT Supplier_Id, Product_Ids FROM Suppliers")
                    for sid, plist in cur.fetchall():
                        lst = _load_json_list(plist)
                        if product_id in lst:
                            lst.remove(product_id)
                            cur.execute("UPDATE Suppliers SET Product_Ids = ? WHERE Supplier_Id = ?", (_dump_json_list(lst), sid))
                    
                    cur.execute("SELECT Category_Id, Product_Ids FROM Category")
                    for cid, plist in cur.fetchall():
                        lst = _load_json_list(plist)
                        if product_id in lst:
                            lst.remove(product_id)
                            if lst:
                                cur.execute("UPDATE Category SET Product_Ids = ? WHERE Category_Id = ?", (_dump_json_list(lst), cid))

                    cur.execute("DELETE FROM Images WHERE Product_Id = ?", (product_id,))
                    cur.execute("DELETE FROM Products WHERE Product_Id = ?", (product_id,))
                    conn.commit()

                    if cur.rowcount == 0:
                        print("Product not found")
                else:
                    print("Please choose: Create, Read, Update, Delete")

            except (ValueError, KeyError) as e:
                print(f"Error: {e}")
        elif class_to_create == "supplier":
            action = input("Supplier: Create, Read, Update, Delete, AddProduct, RemoveProduct: ").strip().lower()
            try:
                if action == "create":
                    name = input("Supplier Name: ").strip()
                    email = input("Supplier Contact Email: ").strip()
                    sid = create_supplier(conn, name, email)
                    print(f"Created Supplier Id: {sid}")
                elif action == "read":
                    sid = input("Supplier Id (UUID): ").strip()
                    s = read_supplier(conn, sid)
                    print({
                        "supplier_id": s.supplier_id,
                        "supplier_name": s.supplier_name,
                        "supplier_contact": s.supplier_contact,
                        "product_ids": s.product_ids,
                    })
                elif action == "update":
                    sid = input("Supplier Id (UUID): ").strip()
                    new_name = input("New Name (blank = no change): ").strip()
                    new_email = input("New Email (blank = no change): ").strip()
                    kwargs = {}
                    if new_name: kwargs["supplier_name"] = new_name
                    if new_email: kwargs["supplier_contact"] = new_email
                    update_supplier(conn, sid, **kwargs)
                    print("Supplier updated")
                elif action == "delete":
                    sid = input("Supplier Id (UUID): ").strip()
                    delete_supplier(conn, sid)
                    print("Supplier deleted (and any linked products/images/categories were cleaned up).")
                elif action == "addproduct":
                    sid = input("Supplier Id (UUID): ").strip()
                    pid = input("Product Id (UUID from 'Products' table): ").strip()
                    add_product_to_supplier(conn, sid, pid)
                    print("Product linked to supplier")
                elif action == "removeproduct":
                    sid = input("Supplier Id (UUID): ").strip()
                    pid = input("Product Id (UUID from 'Products' table): ").strip()
                    remove_product_from_supplier(conn, sid, pid)
                    print("Product unlinked from supplier")
                else:
                    print("Please choose: Create, Read, Update, Delete, AddProduct, RemoveProduct")
            except (ValueError, KeyError) as e:
                print(f"Error: {e}")
        
        
        elif class_to_create == "category":

            command = input("Category Class: Create, Read, Update, Delete: ")
            command = command.replace(" ", "").lower()

            if command == "create":
                items = input("Enter your category_name, category_desc, and product id. (Can leave null): ")

                parts = [p.strip() for p in items.split(",")]

                while len(parts) < 3:
                    parts.append("")
                name, desc, product_ids = parts

                new_id = str(uuid.uuid4())
                cur.execute("INSERT INTO Category (Category_Id,Category_Name,Category_Description,Product_Ids) VALUES (?,?,?,?)", (new_id,name,desc,product_ids))
                conn.commit()
                print(f"ID of created Category: {new_id}")

            elif command == "read":
                cur.execute("SELECT * FROM Category")
                rows = cur.fetchall()
                for row in rows:
                    print(row)

            elif command == "update":
                cat_id = input("Enter the Category Id: ").strip()

                name = input("Enter new Category Name (leave blank to keep current): ").strip()
                desc = input("Enter new Category Description (leave blank to keep current): ").strip()
                product_ids = input("Enter new Product Ids (comma-separated, leave blank to keep current): ").strip()

                updates = []
                values = []

                if name:
                    updates.append("Category_Name = ?")
                    values.append(name)

                if desc:
                    updates.append("Category_Description = ?")
                    values.append(desc)

                if product_ids:
                    updates.append("Product_Ids = ?")
                    values.append(product_ids)

                if updates:
                    values.append(cat_id)
                    sql = f"UPDATE Category SET {', '.join(updates)} WHERE Category_Id = ?"
                    cur.execute(sql, tuple(values))
                    conn.commit()

                    if cur.rowcount == 0:
                        print("Category Id does not exist")
                    else:
                        print(f"Category {cat_id} updated")
                else:
                    print("No updates provided")


            elif command == "delete":
                id = input("Enter the Category Id: ")
                cur.execute(f"DELETE FROM Category WHERE Category_Id = ? ",(id,))
                conn.commit()
                
                if cur.rowcount == 0:
                    print("Category Id does not exist")
                else:
                    print(f"Category with Id {id} Deleted")
                    # Delete from products as well 
                    cur.execute("""
                        DELETE FROM Products
                        WHERE ',' || Product_Id || ',' LIKE '%,' || ? || ',%'
                    """, (id,))
                    conn.commit()

            else:
                print("Please select a valid command")

        elif class_to_create == "image":

            command = input("Category Class: Create, Read, Update, Delete")
            command = command.replace(" ", "").lower()

            if command == "create":
                product_id = input("Enter Product Id: ").strip()
                image_url = input("Enter Image URL: ").strip()

                # Verify product_id exists in product table 
                cur.execute("SELECT Product_Id FROM Products where Product_Id = ? ",(product_id))
                res = cur.fetchone()

                if not res:
                    print("Product Id does not exist. Cannot create image.")
                    continue
                image_id = str(uuid.uuid4())  # or let SQLite default generate it
                cur.execute("""
                    INSERT INTO Images (Image_Id, Product_Id, Image_URL)
                    VALUES (?, ?, ?)
                """, (image_id, product_id, image_url))
                conn.commit()
                print("Created Image with ID:", image_id)
            elif command == "read":
                    cur.execute("SELECT * FROM Images")
                    rows = cur.fetchall()
                    for row in rows:
                        print(row)
            elif command == "update":
                    image_id = input("Enter Image Id to update: ").strip()
                    new_url = input("Enter new Image URL: ").strip()
                    new_product_id = input("Enter new product Id: ").strip()

                    # Verify product_id exists in product table 
                    if new_product_id:
                        cur.execute("SELECT Product_Id FROM Products where Product_Id = ? ",(new_product_id,))
                        res = cur.fetchone()

                        if not res:
                            print("Product Id does not exist. Cannot create image.")
                            continue
                        
                        cur.execute("UPDATE Images SET Image_URL = ?,Product_Id=? WHERE Image_Id = ?", (new_url,new_product_id, image_id))
                        conn.commit()
                        if cur.rowcount == 0:
                            print("Image Id not found")
                        else:
                            print("Image updated")
                        continue

                    cur.execute("UPDATE Images SET Image_URL = ? WHERE Image_Id = ?", (new_url, image_id))
                    conn.commit()
                    if cur.rowcount == 0:
                        print("Image Id not found")
                    else:
                        print("Image updated")
                          
            elif command == "delete":
                    image_id = input("Enter Image Id to delete: ").strip()
                    cur.execute("DELETE FROM Images WHERE Image_Id = ?", (image_id,))
                    conn.commit()
                    # Also make sure it gets deleted from products 

                    if cur.rowcount == 0:
                        print("Image Id not found")
                    else:
                        print("Image deleted")
                        # Delete from products as well 
                        cur.execute("""
                            DELETE FROM Products
                            WHERE ',' || Image_Ids || ',' LIKE '%,' || ? || ',%'
                        """, (image_id,))
                        conn.commit()
            else:
                print("Please select a valid command")

        else:
            print("Please select an option from (Product, Image, Supplier, or Category)")
