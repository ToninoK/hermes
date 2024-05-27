from src.db.connection import conn

async def fetch_stores():
    async with conn.cursor() as cur:
        await cur.execute('SELECT * FROM stores')
        stores = await cur.fetchall()
        return [dict(store) for store in stores]
