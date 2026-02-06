"""
Synthetic Data Generator for Migration System Testing
======================================================
Creates realistic source and target databases with:
- Different schemas
- Renamed columns
- Changed data types
- Split/merged fields
"""

import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)

# Simple data generators
FIRST_NAMES = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 'James', 'Mary',
               'William', 'Patricia', 'Richard', 'Jennifer', 'Joseph', 'Linda', 'Thomas', 'Barbara']
LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'email.com']
PRODUCT_PREFIXES = ['Super', 'Ultra', 'Mega', 'Premium', 'Deluxe', 'Pro', 'Elite', 'Advanced']
PRODUCT_TYPES = ['Widget', 'Gadget', 'Tool', 'Device', 'System', 'Solution', 'Kit', 'Package']


def generate_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def generate_email(name):
    name_part = name.lower().replace(' ', '.')
    return f"{name_part}@{random.choice(DOMAINS)}"


def generate_phone():
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def generate_product():
    return f"{random.choice(PRODUCT_PREFIXES)} {random.choice(PRODUCT_TYPES)}"


def create_source_database(db_path: str):
    """Create source database with legacy schema"""

    # Remove existing database file
    import os
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"   Removed existing database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Customers table (legacy schema)
    cursor.execute('''
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email_address TEXT,
            phone_number TEXT,
            registration_date DATE,
            customer_status TEXT
        )
    ''')

    # Orders table (legacy schema)
    cursor.execute('''
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date DATE,
            total_amount REAL,
            order_status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')

    # Products table (legacy schema)
    cursor.execute('''
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            product_category TEXT,
            unit_price REAL,
            stock_quantity INTEGER
        )
    ''')

    # Order Items table (legacy schema)
    cursor.execute('''
        CREATE TABLE order_items (
            item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            item_price REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Generate customer data
    print("Generating customer data...")
    customers_data = []
    for i in range(1, 101):
        name = generate_name()
        customers_data.append((
            i,
            name,
            generate_email(name),
            generate_phone(),
            (datetime.now() - timedelta(days=random.randint(0, 1095))).strftime('%Y-%m-%d'),
            random.choice(['Active', 'Inactive', 'Suspended'])
        ))

    cursor.executemany(
        'INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)',
        customers_data
    )

    # Generate products data
    print("Generating product data...")
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home & Garden']
    products_data = []
    for i in range(1, 51):
        products_data.append((
            i,
            generate_product(),
            random.choice(categories),
            round(random.uniform(10, 500), 2),
            random.randint(0, 1000)
        ))

    cursor.executemany(
        'INSERT INTO products VALUES (?, ?, ?, ?, ?)',
        products_data
    )

    # Generate orders data
    print("Generating order data...")
    orders_data = []
    for i in range(1, 201):
        orders_data.append((
            i,
            random.randint(1, 100),
            (datetime.now() - timedelta(days=random.randint(0, 730))).strftime('%Y-%m-%d'),
            round(random.uniform(50, 2000), 2),
            random.choice(['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'])
        ))

    cursor.executemany(
        'INSERT INTO orders VALUES (?, ?, ?, ?, ?)',
        orders_data
    )

    # Generate order items data
    print("Generating order items data...")
    order_items_data = []
    item_id = 1
    for order_id in range(1, 201):
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            product_id = random.randint(1, 50)
            quantity = random.randint(1, 10)
            # Get product price
            cursor.execute('SELECT unit_price FROM products WHERE product_id = ?', (product_id,))
            unit_price = cursor.fetchone()[0]

            order_items_data.append((
                item_id,
                order_id,
                product_id,
                quantity,
                round(unit_price * quantity, 2)
            ))
            item_id += 1

    cursor.executemany(
        'INSERT INTO order_items VALUES (?, ?, ?, ?, ?)',
        order_items_data
    )

    conn.commit()
    conn.close()
    print(f"✅ Source database created: {db_path}")


def create_target_database(db_path: str):
    """Create target database with modernized schema"""

    # Remove existing database file
    import os
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"   Removed existing database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clients table (modernized - customers split into first/last name)
    cursor.execute('''
        CREATE TABLE clients (
            client_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            contact_phone TEXT,
            registration_timestamp TEXT,
            account_state TEXT
        )
    ''')

    # Purchases table (modernized - orders renamed)
    cursor.execute('''
        CREATE TABLE purchases (
            purchase_id INTEGER PRIMARY KEY,
            client_id INTEGER,
            purchase_timestamp TEXT,
            total_cost REAL,
            purchase_state TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
    ''')

    # Items table (modernized - products renamed)
    cursor.execute('''
        CREATE TABLE items (
            item_id INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            item_category TEXT,
            price REAL,
            stock_count INTEGER
        )
    ''')

    # Purchase Details table (modernized - order_items renamed)
    cursor.execute('''
        CREATE TABLE purchase_details (
            detail_id INTEGER PRIMARY KEY,
            purchase_id INTEGER,
            item_id INTEGER,
            qty INTEGER,
            line_total REAL,
            FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Target database created: {db_path}")


def create_databases():
    """Create both source and target databases"""
    source_db = '/Users/ayushigupta/Documents/GitHub/DataForge/track2/outputs/source_database.db'
    target_db = '/Users/ayushigupta/Documents/GitHub/DataForge/track2/outputs/target_database.db'
    
    print("="*80)
    print("Creating Synthetic Databases for Migration Testing")
    print("=" * 80)
    print()

    print("📊 Creating source database (legacy schema)...")
    create_source_database(source_db)

    print()
    print("📊 Creating target database (modernized schema)...")
    create_target_database(target_db)

    print()
    print("=" * 80)
    print("✨ Database creation complete!")
    print("=" * 80)
    print(f"\nSource DB: {source_db}")
    print(f"Target DB: {target_db}")
    print()
    print("Schema Differences:")
    print("  - customers → clients (table renamed)")
    print("  - full_name → first_name + last_name (field split)")
    print("  - email_address → email (column renamed)")
    print("  - registration_date → registration_timestamp (type change)")
    print("  - customer_status → account_state (column renamed)")
    print("  - orders → purchases (table renamed)")
    print("  - products → items (table renamed)")
    print("  - order_items → purchase_details (table renamed)")
    print()

    return source_db, target_db


if __name__ == "__main__":
    create_databases()