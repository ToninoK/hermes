"""
create stores and employees table and insert seed data for stores
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """CREATE TABLE stores (
            id SERIAL PRIMARY KEY,
            city VARCHAR(256),
            country VARCHAR(256)
        )""",
        "DROP TABLE stores",
    ),
    step(
        """INSERT INTO stores (city, country) VALUES 
        ('New York', 'USA'),
        ('Los Angeles', 'USA'),
        ('Chicago', 'USA'),
        ('Houston', 'USA'),
        ('Phoenix', 'USA'),
        ('London', 'UK'),
        ('Manchester', 'UK'),
        ('Birmingham', 'UK'),
        ('Paris', 'France'),
        ('Lyon', 'France'),
        ('Tokyo', 'Japan'),
        ('Osaka', 'Japan'),
        ('Nagoya', 'Japan'),
        ('Berlin', 'Germany'),
        ('Munich', 'Germany');
    """
    ),
    step(
        """CREATE TABLE employees (
            id SERIAL PRIMARY KEY,
            email VARCHAR(256) UNIQUE,
            password VARCHAR(256),
            role VARCHAR(256),
            name VARCHAR(256),
            store_id INTEGER REFERENCES stores(id)
        )""",
        "DROP TABLE employees",
    ),
]
