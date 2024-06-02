"""
create reporting tables
"""

from yoyo import step

__depends__ = {'20240527_01_7NG6b-create-users-table'}

steps = [
    step(
        """CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(256),
            category VARCHAR(256),
            price FLOAT
        )""",
        "DROP TABLE products",
    ),
    step(
        """CREATE TABLE inventory (
            product_id INTEGER REFERENCES products(id),
            store_id INTEGER REFERENCES stores(id),
            quantity INTEGER
        )""",
        "DROP TABLE inventory",
    ),
    step(
        """CREATE TABLE sales (
            id SERIAL PRIMARY KEY,
            store_id INTEGER REFERENCES stores(id),
            product_id INTEGER REFERENCES products(id),
            order_quantity INTEGER,
            employee_id INTEGER REFERENCES employees(id),
            date DATE DEFAULT CURRENT_DATE
        )""",
        "DROP TABLE sales",
    ),
]
