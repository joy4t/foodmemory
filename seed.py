import asyncio
import sys
sys.path.insert(0, '.')
import aiosqlite
from backend.database import init_db

async def seed():
    await init_db()
    async with aiosqlite.connect('data/food_memory.db') as db:
        await db.execute("INSERT OR IGNORE INTO users (id, name) VALUES ('demo-user', 'Joy')")
        await db.execute("""
            INSERT OR IGNORE INTO ratings 
            (id, user_id, order_item_id, restaurant_id, score, note, would_reorder, rated_at)
            VALUES 
            ('r1','demo-user','chicken_biryani','mgn001',5,'Best biryani in Bangalore, smoky and perfectly spiced',1,'2026-05-10'),
            ('r2','demo-user','paneer_butter_masala','mgn001',3,'Too sweet for my taste',0,'2026-05-12'),
            ('r3','demo-user','chicken_65','mgn001',4,'Crispy and well spiced, good starter',1,'2026-05-15')
        """)
        await db.commit()
        print('Seeded!')
        async with db.execute("SELECT order_item_id, score, note FROM ratings WHERE user_id='demo-user'") as cursor:
            rows = await cursor.fetchall()
            for r in rows:
                print(f'  {r[0]}: {r[1]}/5 - {r[2]}')

asyncio.run(seed())