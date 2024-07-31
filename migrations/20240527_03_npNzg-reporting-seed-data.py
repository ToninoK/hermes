"""
reporting seed data
"""

from yoyo import step

__depends__ = {"20240527_02_P0EDn-create-reporting-tables"}

steps = [
    step(
        """INSERT INTO products (name, category, price) VALUES 
        ('Laptop', 'Electronics', 999.99),
        ('Smartphone', 'Electronics', 499.99),
        ('Tablet', 'Electronics', 299.99),
        ('Smartwatch', 'Electronics', 199.99),
        ('Desk Chair', 'Furniture', 89.99),
        ('Office Desk', 'Furniture', 129.99),
        ('Coffee Maker', 'Appliances', 29.99),
        ('Blender', 'Appliances', 49.99),
        ('Notebook', 'Stationery', 2.99),
        ('Pen', 'Stationery', 1.49),
        ('Backpack', 'Accessories', 39.99),
        ('Sunglasses', 'Accessories', 79.99),
        ('Headphones', 'Electronics', 149.99),
        ('Mouse', 'Electronics', 24.99),
        ('Keyboard', 'Electronics', 49.99);
    """,
        "ALTER SEQUENCE products_id_seq RESTART WITH 1;",
    ),
    step(
        """INSERT INTO employees (email, name, store_id, role, password) VALUES 
        ('john.doe@example.com', 'John Doe', 1, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('jane.smith@example.com', 'Jane Smith', 1, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('alice.johnson@example.com', 'Alice Johnson', 2, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('bob.brown@example.com', 'Bob Brown', 2, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('charlie.davis@example.com', 'Charlie Davis', 3, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('diana.evans@example.com', 'Diana Evans', 3, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('frank.garcia@example.com', 'Frank Garcia', 4, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('grace.harris@example.com', 'Grace Harris', 4, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('henry.ian@example.com', 'Henry Ian', 5, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('isabel.jackson@example.com', 'Isabel Jackson', 5, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('jack.king@example.com', 'Jack King', 6, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('karen.lewis@example.com', 'Karen Lewis', 6, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('leo.miller@example.com', 'Leo Miller', 7, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('mia.nelson@example.com', 'Mia Nelson', 7, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('nina.owens@example.com', 'Nina Owens', 8, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('oliver.perez@example.com', 'Oliver Perez', 8, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('paul.quinn@example.com', 'Paul Quinn', 9, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('quincy.robinson@example.com', 'Quincy Robinson', 9, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('rachel.smith@example.com', 'Rachel Smith', 10, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('steve.thompson@example.com', 'Steve Thompson', 10, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('tina.underwood@example.com', 'Tina Underwood', 11, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('ursula.vasquez@example.com', 'Ursula Vasquez', 11, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('victor.williams@example.com', 'Victor Williams', 12, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('wendy.xavier@example.com', 'Wendy Xavier', 12, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('xander.young@example.com', 'Xander Young', 13, 'store_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('yvonne.zimmer@example.com', 'Yvonne Zimmer', 13, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('zachary.adams@example.com', 'Zachary Adams', 14, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('amelia.baker@example.com', 'Amelia Baker', 14, true, '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('bruce.clark@example.com', 'Bruce Clark', 15, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('diana.evans2@example.com', 'Diana Evans', 15, 'employee', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u'),
        ('hermes@example.com', 'Hermes', 1, 'company_manager', '$2b$12$SOmiJQiZgbP4n7EMYfDZ/Oaru158ZTgpsWshpC8qVcWSa.hoy1C3u');
    """,
        "ALTER SEQUENCE employees_id_seq RESTART WITH 1;",
    ),
    step(
        """INSERT INTO inventory (product_id, store_id, quantity) VALUES 
        (1, 1, 50),
        (2, 1, 100),
        (3, 2, 30),
        (4, 2, 20),
        (5, 3, 15),
        (6, 3, 40),
        (7, 4, 25),
        (8, 4, 10),
        (9, 5, 200),
        (10, 5, 150),
        (11, 6, 35),
        (12, 6, 25),
        (13, 7, 60),
        (14, 7, 80),
        (15, 8, 50),
        (1, 9, 70),
        (2, 9, 120),
        (3, 10, 40),
        (4, 10, 10),
        (5, 11, 100),
        (6, 11, 30),
        (7, 12, 20),
        (8, 12, 15),
        (9, 13, 300),
        (10, 13, 200),
        (11, 14, 40),
        (12, 14, 35),
        (13, 15, 75),
        (14, 15, 90),
        (15, 15, 60);
    """
    ),
    step(
        """INSERT INTO sales (store_id, product_id, order_quantity, employee_id, date) VALUES 
        (1, 1, 1, 1, '2024-05-20'),
        (1, 2, 2, 2, '2024-05-19'),
        (2, 3, 1, 3, '2024-05-18'),
        (2, 4, 3, 4, '2024-05-17'),
        (3, 5, 5, 5, '2024-05-16'),
        (3, 6, 2, 6, '2024-05-17'),
        (4, 7, 1, 7, '2024-05-18'),
        (4, 8, 1, 8, '2024-05-19'),
        (5, 9, 3, 9, '2024-05-20'),
        (5, 10, 2, 10, '2024-05-21'),
        (6, 11, 4, 11, '2024-05-22'),
        (6, 12, 1, 12, '2024-05-23'),
        (7, 13, 2, 13, '2024-05-22'),
        (7, 14, 1, 14, '2024-05-25'),
        (8, 15, 1, 15, '2024-05-21'),
        (8, 1, 3, 16, '2024-05-27'),
        (9, 2, 1, 17, '2024-05-28'),
        (9, 3, 2, 18, '2024-05-27'),
        (10, 4, 1, 19, '2024-05-27'),
        (10, 5, 2, 20, '2024-05-31'),
        (11, 6, 1, 21, '2024-06-01'),
        (11, 7, 2, 22, '2024-06-01'),
        (12, 8, 1, 23, '2024-06-01'),
        (12, 9, 3, 24, '2024-05-15'),
        (13, 10, 2, 25, '2024-05-15'),
        (13, 11, 1, 26, '2024-05-16'),
        (14, 12, 1, 27, '2024-05-17'),
        (15, 14, 1, 29, '2024-05-22'),
        (15, 15, 3, 30, '2024-05-10');
    """,
        "ALTER SEQUENCE sales_id_seq RESTART WITH 1;",
    ),
]
