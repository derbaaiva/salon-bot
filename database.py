import aiosqlite

DB = "salon.db"

async def init_db():
async with aiosqlite.connect(DB) as db:

```
    # Услуги
    await db.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        duration INTEGER
    )
    """)

    # Мастера
    await db.execute("""
    CREATE TABLE IF NOT EXISTS masters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    # Какие услуги оказывает мастер
    await db.execute("""
    CREATE TABLE IF NOT EXISTS master_services (
        master_id INTEGER,
        service_id INTEGER
    )
    """)

    # Записи клиентов
    await db.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        service_id INTEGER,
        master_id INTEGER,
        date TEXT,
        time TEXT,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Тестовые услуги
    cur = await db.execute(
        "SELECT COUNT(*) FROM services"
    )

    count = (await cur.fetchone())[0]

    if count == 0:

        await db.executemany(
            """
            INSERT INTO services
            (name, price, duration)
            VALUES (?, ?, ?)
            """,
            [
                ("Маникюр", 500, 90),
                ("Педикюр", 700, 120),
                ("Стрижка", 300, 60)
            ]
        )

    # Тестовые мастера
    cur = await db.execute(
        "SELECT COUNT(*) FROM masters"
    )

    count = (await cur.fetchone())[0]

    if count == 0:

        await db.executemany(
            """
            INSERT INTO masters (name)
            VALUES (?)
            """,
            [
                ("Аня",),
                ("Катя",),
                ("Оля",)
            ]
        )

    # Связка мастер-услуга
    cur = await db.execute(
        "SELECT COUNT(*) FROM master_services"
    )

    count = (await cur.fetchone())[0]

    if count == 0:

        await db.executemany(
            """
            INSERT INTO master_services
            (master_id, service_id)
            VALUES (?, ?)
            """,
            [
                (1, 1),
                (1, 2),

                (2, 1),
                (2, 3),

                (3, 2),
                (3, 3)
            ]
        )

    await db.commit()
```

# Услуги

async def get_services():

```
async with aiosqlite.connect(DB) as db:

    cur = await db.execute("""
        SELECT id, name, price
        FROM services
    """)

    return await cur.fetchall()
```

# Мастера по услуге

async def get_masters_by_service(service_id):

```
async with aiosqlite.connect(DB) as db:

    cur = await db.execute("""
        SELECT m.id, m.name
        FROM masters m
        JOIN master_services ms
        ON ms.master_id = m.id
        WHERE ms.service_id = ?
    """, (service_id,))

    return await cur.fetchall()
```

# Занятые слоты

async def get_booked(master_id, date):

```
async with aiosqlite.connect(DB) as db:

    cur = await db.execute("""
        SELECT time
        FROM bookings
        WHERE master_id=?
        AND date=?
        AND status='ACTIVE'
    """, (master_id, date))

    rows = await cur.fetchall()

    return [r[0] for r in rows]
```

# Создание записи

async def add_booking(
user_id,
username,
service_id,
master_id,
date,
time
):

```
async with aiosqlite.connect(DB) as db:

    cur = await db.execute("""
        SELECT id
        FROM bookings
        WHERE master_id=?
        AND date=?
        AND time=?
        AND status='ACTIVE'
    """, (
        master_id,
        date,
        time
    ))

    if await cur.fetchone():
        return False

    await db.execute("""
        INSERT INTO bookings (
            user_id,
            username,
            service_id,
            master_id,
            date,
            time
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        username,
        service_id,
        master_id,
        date,
        time
    ))

    await db.commit()

    return True
```

# Записи клиента

async def get_user_bookings(user_id):

```
async with aiosqlite.connect(DB) as db:

    cur = await db.execute("""
        SELECT
            b.id,
            s.name,
            m.name,
            b.date,
            b.time
        FROM bookings b
        JOIN services s
            ON s.id=b.service_id
        JOIN masters m
            ON m.id=b.master_id
        WHERE b.user_id=?
        AND b.status='ACTIVE'
        ORDER BY b.date, b.time
    """, (user_id,))

    return await cur.fetchall()
```

# Отмена записи

async def cancel_booking(booking_id):

```
async with aiosqlite.connect(DB) as db:

    await db.execute("""
        UPDATE bookings
        SET status='CANCELLED'
        WHERE id=?
    """, (booking_id,))

    await db.commit()
```

# Все записи

async def get_all_bookings():

```
async with aiosqlite.connect(DB) as db:

    cur = await db.execute("""
        SELECT
            b.id,
            s.name,
            m.name,
            b.date,
            b.time,
            b.status
        FROM bookings b
        JOIN services s
            ON s.id=b.service_id
        JOIN masters m
            ON m.id=b.master_id
        ORDER BY b.date, b.time
    """)

    return await cur.fetchall()
```

# Доходы мастеров

async def get_income_stats():

```
async with aiosqlite.connect(DB) as db:

    cur = await db.execute("""
        SELECT
            m.name,
            COUNT(*),
            SUM(s.price)
        FROM bookings b
        JOIN masters m
            ON m.id=b.master_id
        JOIN services s
            ON s.id=b.service_id
        WHERE b.status='ACTIVE'
        GROUP BY m.id
    """)

    return await cur.fetchall()
```
