import aiosqlite
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "food_memory.db")


async def get_db() -> aiosqlite.Connection:
    """Get a database connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Create all tables if they don't exist."""
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                swiggy_order_id TEXT,
                restaurant_id TEXT NOT NULL,
                restaurant_name TEXT NOT NULL,
                order_total REAL NOT NULL DEFAULT 0,
                ordered_at TEXT NOT NULL DEFAULT (datetime('now')),
                status TEXT NOT NULL DEFAULT 'placed'
                    CHECK (status IN ('placed', 'delivered', 'cancelled'))
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL REFERENCES orders(id),
                item_name TEXT NOT NULL,
                item_id TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                price REAL NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS ratings (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                order_item_id TEXT NOT NULL REFERENCES order_items(id),
                restaurant_id TEXT NOT NULL,
                score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
                note TEXT,
                would_reorder INTEGER NOT NULL DEFAULT 1,
                rated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS implicit_signals (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                item_name TEXT NOT NULL,
                restaurant_id TEXT NOT NULL,
                signal_type TEXT NOT NULL
                    CHECK (signal_type IN ('reorder', 'skip', 'cart_remove', 'browse_only')),
                count INTEGER NOT NULL DEFAULT 1,
                last_seen TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- Indexes for common queries
            CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
            CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
            CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
            CREATE INDEX IF NOT EXISTS idx_ratings_restaurant ON ratings(restaurant_id);
            CREATE INDEX IF NOT EXISTS idx_signals_user_item ON implicit_signals(user_id, item_name);
        """)
        await db.commit()
        print("✅ Database initialized successfully")
    finally:
        await db.close()
