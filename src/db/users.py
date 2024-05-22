from src.db.connection import conn


async def create_user(user):
    q = """
    INSERT INTO users (email, password, role)
    VALUES (%s, %s, %s)
    RETURNING *
    """
    async with conn.cursor() as cursor:
        await cursor.execute(q, (user["email"], user["password"], "unknown"))
        result = await cursor.fetchone()
        return dict(result) if result else None


async def get_user_by_email(email):
    q = """SELECT * FROM users WHERE email=%s"""
    async with conn.cursor() as cursor:
        await cursor.execute(q, (email,))
        result = await cursor.fetchone()
        return dict(result) if result else None
