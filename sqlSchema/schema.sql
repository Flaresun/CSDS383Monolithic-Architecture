CREATE TABLE Products (
    Product_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    Product_Name VARCHAR(2000) NOT NULL,
    Product_Description VARCHAR(10000),
    Product_Quantity INT NOT NULL CHECK (Product_Quantity >= 0),
    Product_Price DECIMAL NOT NULL CHECK (Product_Price > 0),
    Supplier_Ids UUID[] DEFAULT '{}', 
    Category_Ids UUID[] DEFAULT '{}', 
    Image_Ids UUID[] DEFAULT '{}'    
);

CREATE TABLE Suppliers (
    Supplier_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    Supplier_Name VARCHAR(2000) NOT NULL,
    Supplier_Contact VARCHAR(320) NOT NULL CHECK (Supplier_Contact ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    Product_Ids UUID[] DEFAULT '{}' 
);

CREATE TABLE Categories (
    Category_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    Category_Name VARCHAR(2000) NOT NULL,
    Category_Description VARCHAR(10000),
    Product_Ids UUID[] DEFAULT '{}' 
);

CREATE TABLE Images (
    Image_Id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    Product_Id UUID NOT NULL,
    Image_URL TEXT NOT NULL
);
