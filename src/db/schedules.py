from src.db.connection import conn


async def create_schedule(frequency, config, email):
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO scheduled_reports(frequency, config, created_by) VALUES (%s, %s, %s) RETURNING *",
            (frequency, config, email),
        )
        schedule = await cur.fetchone()
        return dict(schedule)


async def get_schedules(frequency, email):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT * FROM scheduled_reports WHERE frequency = %s AND created_by=%s",
            (frequency, email),
        )
        results = await cur.fetchall()
        return [dict(schedule) for schedule in results]


async def get_schedules_all(frequency):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT * FROM scheduled_reports WHERE frequency = %s", (frequency,)
        )
        results = await cur.fetchall()
        return [dict(schedule) for schedule in results]
