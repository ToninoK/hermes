"""
create users table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """CREATE TABLE users(
            id SERIAL PRIMARY KEY,
            email VARCHAR(256) UNIQUE,
            password VARCHAR(512),
            role VARCHAR(256)
        )
        """,
        """DROP TABLE users""",
    )
]
