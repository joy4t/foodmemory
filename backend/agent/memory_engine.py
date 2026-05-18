"""
Memory Engine — queries and updates the user's food memory.

Handles:
- Fetching past ratings for a restaurant/item
- Recording new ratings and orders
- Tracking implicit signals (reorder frequency, skips)
- Building memory context for the LLM prompt
"""

import uuid
from datetime import datetime
from backend.database import get_db


class MemoryEngine:
    def __init__(self):
        pass

    # ─── User Management ───

    async def ensure_user(self, user_id: str, name: str = "User") -> str:
        """Create user if doesn't exist, return user_id."""
        db = await get_db()
        try:
            row = await db.execute(
                "SELECT id FROM users WHERE id = ?", (user_id,)
            )
            existing = await row.fetchone()
            if existing:
                return user_id

            await db.execute(
                "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
                (user_id, name, f"{user_id}@foodmemory.local"),
            )
            await db.commit()
            return user_id
        finally:
            await db.close()

    # ─── Order Recording ───

    async def record_order(
        self,
        user_id: str,
        restaurant_id: str,
        restaurant_name: str,
        items: list[dict],
        swiggy_order_id: str = None,
    ) -> str:
        """Record a new order and its items. Returns order_id."""
        await self.ensure_user(user_id)
        db = await get_db()
        try:
            order_id = str(uuid.uuid4())
            order_total = sum(
                item.get("price", 0) * item.get("quantity", 1) for item in items
            )

            await db.execute(
                """INSERT INTO orders (id, user_id, swiggy_order_id, restaurant_id,
                   restaurant_name, order_total, status)
                   VALUES (?, ?, ?, ?, ?, ?, 'placed')""",
                (order_id, user_id, swiggy_order_id, restaurant_id,
                 restaurant_name, order_total),
            )

            for item in items:
                item_id = str(uuid.uuid4())
                await db.execute(
                    """INSERT INTO order_items (id, order_id, item_name, item_id,
                       quantity, price)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (item_id, order_id, item["name"], item.get("item_id", ""),
                     item.get("quantity", 1), item.get("price", 0)),
                )

                # Record implicit reorder signal
                await self._update_signal(
                    db, user_id, item["name"], restaurant_id, "reorder"
                )

            await db.commit()
            return order_id
        finally:
            await db.close()

    # ─── Rating Management ───

    async def record_rating(
        self,
        user_id: str,
        order_item_id: str,
        restaurant_id: str,
        score: int,
        note: str = None,
        would_reorder: bool = True,
    ) -> str:
        """Store a new rating. Returns rating_id."""
        await self.ensure_user(user_id)
        db = await get_db()
        try:
            rating_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO ratings (id, user_id, order_item_id, restaurant_id,
                   score, note, would_reorder)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (rating_id, user_id, order_item_id, restaurant_id,
                 score, note, 1 if would_reorder else 0),
            )
            await db.commit()
            return rating_id
        finally:
            await db.close()

    async def quick_rate(
        self,
        user_id: str,
        item_name: str,
        restaurant_id: str,
        restaurant_name: str,
        score: int,
        note: str = None,
        would_reorder: bool = True,
    ) -> str:
        """Quick-rate a dish without needing an existing order.
        Creates an order + order_item + rating in one call.
        Used when user rates a dish conversationally."""
        await self.ensure_user(user_id)
        db = await get_db()
        try:
            # Create a virtual order
            order_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO orders (id, user_id, restaurant_id, restaurant_name,
                   order_total, status)
                   VALUES (?, ?, ?, ?, 0, 'delivered')""",
                (order_id, user_id, restaurant_id, restaurant_name),
            )

            # Create a virtual order item
            order_item_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO order_items (id, order_id, item_name, quantity, price)
                   VALUES (?, ?, ?, 1, 0)""",
                (order_item_id, order_id, item_name),
            )

            # Create the rating
            rating_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO ratings (id, user_id, order_item_id, restaurant_id,
                   score, note, would_reorder)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (rating_id, user_id, order_item_id, restaurant_id,
                 score, note, 1 if would_reorder else 0),
            )

            await db.commit()
            return rating_id
        finally:
            await db.close()

    # ─── Memory Queries ───

    async def get_restaurant_memory(self, user_id: str, restaurant_id: str) -> dict:
        """Get all memory (ratings + signals) for a user at a restaurant."""
        db = await get_db()
        try:
            # Get ratings
            cursor = await db.execute(
                """SELECT r.score, r.note, r.would_reorder, r.rated_at,
                          oi.item_name
                   FROM ratings r
                   JOIN order_items oi ON r.order_item_id = oi.id
                   WHERE r.user_id = ? AND r.restaurant_id = ?
                   ORDER BY r.rated_at DESC""",
                (user_id, restaurant_id),
            )
            rows = await cursor.fetchall()
            ratings = [
                {
                    "item_name": row[4],
                    "score": row[0],
                    "note": row[1],
                    "would_reorder": bool(row[2]),
                    "rated_at": row[3],
                }
                for row in rows
            ]

            # Get implicit signals
            cursor = await db.execute(
                """SELECT item_name, signal_type, count, last_seen
                   FROM implicit_signals
                   WHERE user_id = ? AND restaurant_id = ?
                   ORDER BY count DESC""",
                (user_id, restaurant_id),
            )
            rows = await cursor.fetchall()
            signals = [
                {
                    "item_name": row[0],
                    "signal_type": row[1],
                    "count": row[2],
                    "last_seen": row[3],
                }
                for row in rows
            ]

            return {"ratings": ratings, "signals": signals}
        finally:
            await db.close()

    async def get_item_memory(self, user_id: str, item_name: str) -> dict:
        """Get memory for a specific dish across all restaurants."""
        db = await get_db()
        try:
            cursor = await db.execute(
                """SELECT r.score, r.note, r.would_reorder, r.rated_at,
                          r.restaurant_id, oi.item_name,
                          o.restaurant_name
                   FROM ratings r
                   JOIN order_items oi ON r.order_item_id = oi.id
                   JOIN orders o ON oi.order_id = o.id
                   WHERE r.user_id = ? AND LOWER(oi.item_name) LIKE ?
                   ORDER BY r.rated_at DESC""",
                (user_id, f"%{item_name.lower()}%"),
            )
            rows = await cursor.fetchall()
            ratings = [
                {
                    "item_name": row[5],
                    "restaurant_name": row[6],
                    "score": row[0],
                    "note": row[1],
                    "would_reorder": bool(row[2]),
                    "rated_at": row[3],
                }
                for row in rows
            ]

            return {"ratings": ratings}
        finally:
            await db.close()

    async def get_all_user_ratings(self, user_id: str) -> list:
        """Get all ratings for a user."""
        db = await get_db()
        try:
            cursor = await db.execute(
                """SELECT r.score, r.note, r.would_reorder, r.rated_at,
                          r.restaurant_id, oi.item_name,
                          o.restaurant_name
                   FROM ratings r
                   JOIN order_items oi ON r.order_item_id = oi.id
                   JOIN orders o ON oi.order_id = o.id
                   WHERE r.user_id = ?
                   ORDER BY r.rated_at DESC
                   LIMIT 20""",
                (user_id,),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "item_name": row[5],
                    "restaurant_name": row[6],
                    "restaurant_id": row[4],
                    "score": row[0],
                    "note": row[1],
                    "would_reorder": bool(row[2]),
                    "rated_at": row[3],
                }
                for row in rows
            ]
        finally:
            await db.close()

    # ─── Context Building ───

    async def build_memory_context(self, user_id: str, restaurant_id: str) -> str:
        """Build a text summary of the user's memory for LLM context."""
        memory = await self.get_restaurant_memory(user_id, restaurant_id)

        if not memory["ratings"] and not memory["signals"]:
            return ""

        lines = []

        if memory["ratings"]:
            lines.append("=== Your past ratings at this restaurant ===")
            for r in memory["ratings"]:
                stars = "⭐" * r["score"]
                line = f"- {r['item_name']}: {stars} ({r['score']}/5)"
                if r["note"]:
                    line += f" — \"{r['note']}\""
                if not r["would_reorder"]:
                    line += " [would NOT reorder]"
                lines.append(line)

        if memory["signals"]:
            lines.append("\n=== Ordering patterns ===")
            for s in memory["signals"]:
                if s["signal_type"] == "reorder" and s["count"] > 1:
                    lines.append(
                        f"- {s['item_name']}: ordered {s['count']} times"
                    )

        return "\n".join(lines)

    async def build_global_context(self, user_id: str) -> str:
        """Build a summary of user's overall food preferences."""
        ratings = await self.get_all_user_ratings(user_id)

        if not ratings:
            return "This user has no food history yet. They're new to FoodMemory."

        lines = ["=== User's food history ==="]

        # Top-rated items
        top = [r for r in ratings if r["score"] >= 4]
        if top:
            lines.append("Loved items:")
            for r in top[:5]:
                line = f"- {r['item_name']} at {r['restaurant_name']}: {'⭐' * r['score']}"
                if r["note"]:
                    line += f" — \"{r['note']}\""
                lines.append(line)

        # Low-rated items
        low = [r for r in ratings if r["score"] <= 2]
        if low:
            lines.append("Didn't enjoy:")
            for r in low[:5]:
                line = f"- {r['item_name']} at {r['restaurant_name']}: {'⭐' * r['score']}"
                if r["note"]:
                    line += f" — \"{r['note']}\""
                lines.append(line)

        return "\n".join(lines)

    # ─── Implicit Signals ───

    async def record_signal(
        self, user_id: str, item_name: str, restaurant_id: str, signal_type: str
    ) -> None:
        """Record an implicit signal (reorder, skip, cart_remove, browse_only)."""
        db = await get_db()
        try:
            await self._update_signal(db, user_id, item_name, restaurant_id, signal_type)
            await db.commit()
        finally:
            await db.close()

    async def _update_signal(
        self, db, user_id: str, item_name: str, restaurant_id: str, signal_type: str
    ) -> None:
        """Insert or increment an implicit signal."""
        cursor = await db.execute(
            """SELECT id, count FROM implicit_signals
               WHERE user_id = ? AND LOWER(item_name) = LOWER(?)
               AND restaurant_id = ? AND signal_type = ?""",
            (user_id, item_name, restaurant_id, signal_type),
        )
        existing = await cursor.fetchone()

        if existing:
            await db.execute(
                """UPDATE implicit_signals
                   SET count = count + 1, last_seen = datetime('now')
                   WHERE id = ?""",
                (existing[0],),
            )
        else:
            await db.execute(
                """INSERT INTO implicit_signals
                   (id, user_id, item_name, restaurant_id, signal_type, count)
                   VALUES (?, ?, ?, ?, ?, 1)""",
                (str(uuid.uuid4()), user_id, item_name, restaurant_id, signal_type),
            )
