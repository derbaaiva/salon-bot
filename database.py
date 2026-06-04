import aiosqlite

DB = "salon.db"


async def init_db():
    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            duration INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS masters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS master_services (
            master_id INTEGER,
            service_id INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            service_id INTEGER,
            master_id INTEGER,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'ACTIVE'
        )
        """)
        cur = await db.execute("SELECT COUNT(*) FROM masters")
        count = (await cur.fetchone())[0]

        if count == 0:
            await db.executemany(
                "INSERT INTO masters (name) VALUES (?)",
                [
                    ("Аня",),
                    ("Катя",),
                    ("Оля",)
                ]
            )
        await db.commit()


async def get_masters():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id, name FROM masters")
        return await cur.fetchall()


async def get_booked(master_id, date):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT time FROM bookings WHERE master_id=? AND date=? AND status='ACTIVE'",
            (master_id, date)
        )
        rows = await cur.fetchall()
        return [r[0] for r in rows]


async def add_booking(user_id, master_id, date, time):
    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("""
        SELECT id FROM bookings
        WHERE master_id=? AND date=? AND time=? AND status='ACTIVE'
        """, (master_id, date, time))

        if await cur.fetchone():
            return False

        await db.execute("""
        INSERT INTO bookings (user_id, master_id, date, time)
        VALUES (?, ?, ?, ?)
        """, (user_id, master_id, date, time))

        await db.commit()
        return True
