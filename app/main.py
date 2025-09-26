import sqlite3
import product
import image
import supplier
import category
conn = sqlite3.connect(":memory:")
cur = conn.cursor()

## Create Product table
cur.execute(""""
        CREATE TABLE Products (
            Product_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            Product_Name VARCHAR(2000) NOT NULL,
            git VARCHAR(10000),
            Product_Quantity INT NOT NULL CHECK (Product_Quantity >= 0),
            Product_Price DECIMAL NOT NULL CHECK (Product_Price > 0),
            Supplier_Ids UUID[] DEFAULT '{}', 
            Category_Ids UUID[] DEFAULT '{}', 
            Image_Ids UUID[] DEFAULT '{}'    
        )
            """)

## Create Supplier table 
cur.execute("""
    CREATE TABLE Suppliers (
        Supplier_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        Supplier_Name VARCHAR(2000) NOT NULL,
        Supplier_Contact VARCHAR(320) NOT NULL CHECK (Supplier_Contact ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
        Product_Ids UUID[] DEFAULT '{}' 
    )
""")

## Create Category data 
cur.execute("""
    CREATE TABLE Categories (
        Category_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        Category_Name VARCHAR(2000) NOT NULL,
        Category_Description VARCHAR(10000),
        Product_Ids UUID[] DEFAULT '{}' 
    )
""")

## Create Image data 
cur.execute("""
    CREATE TABLE Images (
        Image_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        Product_Id UUID NOT NULL,
        Image_URL TEXT NOT NULL
    )
""")

# Init Classes 
Product = product()
Category = category()
Image = image()
Supplier = supplier()

# CLI Loop
if __name__ == "__main__":
    print("************************************ CLI RUNNING ************************************")
    while True:
        pass