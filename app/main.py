import uuid 
import sqlite3
import product
import image
import supplier
import category
conn = sqlite3.connect(":memory:")
cur = conn.cursor()

## Create Product table
cur.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        Product_Id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        Product_Name TEXT NOT NULL,
        Git TEXT,
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
    CREATE TABLE IF NOT EXISTS Categories (
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
    print("************************************ CLI RUNNING ************************************")
    while True:
        class_to_create  = str(input("What would you like to add? (Product, Image, Supplier, or Category): "))
        class_to_create = class_to_create.replace(" ", "").lower()
        
        if class_to_create == "product":
            Product = product()
        
        elif class_to_create == "supplier":
            Supplier = supplier()
        
        
        elif class_to_create == "category":
            Category = category()

            command = str(input("Category Class: Create, Read, Update, Delete"))
            command = command.replace(" ", "").lower()

            if command == "create":
                items = input("Enter your category_name, category_desc, and product id. (Can leave null)")

                parts = [p.strip() for p in items.split(",")]

                while len(parts) < 3:
                    parts.append("")
                name, desc, product_ids = parts

                new_id = str(uuid.uuid4())
                cur.execute("INSERT INTO Category (Category_Id,Category_Name,Category_Description,Product_Ids) VALUES (?,?,?,?)", (new_id,name,desc,product_ids))
                conn.commit()
                print(f"ID of created Category: {new_id}")

            elif command == "read":
                id = input("Enter the Category Id")
                cur.execute(f"SELECT Category_Id FROM Category WHERE Category_Id = ? ",(id,))
                row = cur.fetchone()
                if not row:
                    print("Category Id does not exist")
                print(f"Category with Id {id} : {row}")

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
                id = input("Enter the Category Id")
                cur.execute(f"DELETE Category_Id FROM Category WHERE Category_Id = ? ",(id,))
                conn.commit()
                
                if cur.rowcount == 0:
                    print("Category Id does not exist")
                else:
                    print(f"Category with Id {id} Deleted")

            else:
                print("Please select a valid command")

        elif class_to_create == "image":
            Image = image()

        else:
            print("Please select an option from (Product, Image, Supplier, or Category)")
