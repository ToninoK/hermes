from src.db.connection import conn


async def fetch_stores():
    async with conn.cursor() as cur:
        await cur.execute('SELECT * FROM stores')
        stores = await cur.fetchall()
        print(stores)
        return [dict(store) for store in stores]


async def fetch_store(store_id):
    async with conn.cursor() as cur:
        await cur.execute('SELECT * FROM stores WHERE id = %s', (store_id,))
        store = await cur.fetchone()
        return dict(store) if store else None
