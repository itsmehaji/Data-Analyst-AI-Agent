"""
Setup script to create sample e-commerce database
"""
import sqlite3
from datetime import datetime, timedelta
import random


def create_sample_database(db_path: str = "sample_data.db"):
    """Create a sample e-commerce database with realistic data"""
    
    print(f"Creating sample database at {db_path}...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS orders")
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            region TEXT NOT NULL,
            signup_date DATE NOT NULL
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INTEGER NOT NULL
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # Create sales table
    cursor.execute("""
        CREATE TABLE sales (
            sale_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            sale_date DATE NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    print("Tables created successfully.")
    
    # Insert sample customers
    regions = ["North", "South", "East", "West"]
    customers_data = []
    for i in range(1, 101):  # 100 customers
        name = f"Customer {i}"
        email = f"customer{i}@example.com"
        region = random.choice(regions)
        signup_date = (datetime.now() - timedelta(days=random.randint(30, 730))).date()
        customers_data.append((i, name, email, region, signup_date))
    
    cursor.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
        customers_data
    )
    print(f"Inserted {len(customers_data)} customers.")
    
    # Insert sample products
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"]
    products_data = [
        (1, "Laptop Pro", "Electronics", 1299.99, 50),
        (2, "Wireless Mouse", "Electronics", 29.99, 200),
        (3, "Running Shoes", "Sports", 89.99, 100),
        (4, "Coffee Maker", "Home & Garden", 79.99, 75),
        (5, "T-Shirt", "Clothing", 19.99, 300),
        (6, "Smartphone", "Electronics", 699.99, 80),
        (7, "Yoga Mat", "Sports", 34.99, 150),
        (8, "Novel Book", "Books", 14.99, 120),
        (9, "Jeans", "Clothing", 59.99, 200),
        (10, "Desk Lamp", "Home & Garden", 39.99, 90),
        (11, "Tablet", "Electronics", 499.99, 60),
        (12, "Backpack", "Sports", 49.99, 180),
        (13, "Cookbook", "Books", 24.99, 100),
        (14, "Sweater", "Clothing", 44.99, 150),
        (15, "Plant Pot", "Home & Garden", 12.99, 250),
    ]
    
    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
        products_data
    )
    print(f"Inserted {len(products_data)} products.")
    
    # Insert sample orders and sales
    order_id = 1
    sale_id = 1
    orders_data = []
    sales_data = []
    
    for customer_id in range(1, 101):  # Each customer makes 0-5 orders
        num_orders = random.randint(0, 5)
        
        for _ in range(num_orders):
            order_date = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
            status = random.choice(["Completed", "Completed", "Completed", "Pending", "Shipped"])
            
            # Each order has 1-4 products
            num_products = random.randint(1, 4)
            order_total = 0
            
            for _ in range(num_products):
                product = random.choice(products_data)
                product_id = product[0]
                unit_price = product[3]
                quantity = random.randint(1, 3)
                total_price = unit_price * quantity
                order_total += total_price
                
                sales_data.append((
                    sale_id,
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    total_price,
                    order_date
                ))
                sale_id += 1
            
            orders_data.append((
                order_id,
                customer_id,
                order_date,
                order_total,
                status
            ))
            order_id += 1
    
    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
        orders_data
    )
    print(f"Inserted {len(orders_data)} orders.")
    
    cursor.executemany(
        "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?)",
        sales_data
    )
    print(f"Inserted {len(sales_data)} sales.")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n✅ Sample database created successfully at {db_path}")
    print("\nDatabase Schema:")
    print("- customers: customer_id, name, email, region, signup_date")
    print("- products: product_id, name, category, price, stock_quantity")
    print("- orders: order_id, customer_id, order_date, total_amount, status")
    print("- sales: sale_id, order_id, product_id, quantity, unit_price, total_price, sale_date")
    print(f"\nTotal records:")
    print(f"  Customers: {len(customers_data)}")
    print(f"  Products: {len(products_data)}")
    print(f"  Orders: {len(orders_data)}")
    print(f"  Sales: {len(sales_data)}")


if __name__ == "__main__":
    create_sample_database()
