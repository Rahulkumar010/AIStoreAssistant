import aioodbc
import asyncio
from config import config
from models import Store, SentimentScorecard, VisualScorecard, Alert, Review, ExecutiveReport
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.dsn = f"Driver={{ODBC Driver 18 for SQL Server}};Server={config.SERVER_NAME};Database={config.DATABASE_NAME};UID={config.USERNAME};PWD={config.PASSWORD};"
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await aioodbc.create_pool(dsn=self.dsn, autocommit=True)

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    # Helper method
    async def _execute(self, query: str, params: tuple = ()):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)

    async def _fetchone(self, query: str, params: tuple = ()):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                row = await cur.fetchone()
                if not row:
                    return None
                columns = [col[0] for col in cur.description]
                return dict(zip(columns, row))

    async def _fetchall(self, query: str, params: tuple = ()):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                rows = await cur.fetchall()
                columns = [col[0] for col in cur.description]
                return [dict(zip(columns, row)) for row in rows]

    # Store operations
    async def create_store(self, store: Store) -> Store:
        query = "INSERT INTO Stores (id, name, location) VALUES (?, ?, ?)"
        await self._execute(query, (store.id, store.name, store.location))
        return store

    async def get_store(self, store_id: str) -> Optional[Store]:
        query = "SELECT * FROM Stores WHERE id = ?"
        row = await self._fetchone(query, (store_id,))
        return Store(**row) if row else None

    async def get_all_stores(self) -> List[Store]:
        query = "SELECT * FROM Stores"
        rows = await self._fetchall(query)
        return [Store(**row) for row in rows]

    async def update_store(self, store_id: str, update_data: Dict[str, Any]):
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        query = f"UPDATE Stores SET {set_clause} WHERE id = ?"
        params = tuple(update_data.values()) + (store_id,)
        await self._execute(query, params)

    async def delete_store(self, store_id: str):
        query = "DELETE FROM Stores WHERE id = ?"
        await self._execute(query, (store_id,))

    # Sentiment Scorecard operations
    async def save_sentiment_scorecard(self, scorecard: SentimentScorecard) -> SentimentScorecard:
        query = """INSERT INTO SentimentScorecards (id, store_id, score, created_at)
                   VALUES (?, ?, ?, ?)"""
        await self._execute(query, (scorecard.id, scorecard.store_id, scorecard.score, scorecard.created_at))
        return scorecard

    async def get_sentiment_scorecards(self, store_id: Optional[str] = None) -> List[SentimentScorecard]:
        query = "SELECT * FROM SentimentScorecards"
        params = ()
        if store_id:
            query += " WHERE store_id = ? ORDER BY created_at DESC"
            params = (store_id,)
        rows = await self._fetchall(query, params)
        return [SentimentScorecard(**row) for row in rows]

    # Visual Scorecard operations
    async def save_visual_scorecard(self, scorecard: VisualScorecard) -> VisualScorecard:
        query = """INSERT INTO VisualScorecards (id, store_id, score, created_at)
                   VALUES (?, ?, ?, ?)"""
        await self._execute(query, (scorecard.id, scorecard.store_id, scorecard.score, scorecard.created_at))
        return scorecard

    async def get_visual_scorecards(self, store_id: Optional[str] = None) -> List[VisualScorecard]:
        query = "SELECT * FROM VisualScorecards"
        params = ()
        if store_id:
            query += " WHERE store_id = ? ORDER BY created_at DESC"
            params = (store_id,)
        rows = await self._fetchall(query, params)
        return [VisualScorecard(**row) for row in rows]

    # Alert operations
    async def create_alert(self, alert: Alert) -> Alert:
        query = """INSERT INTO Alerts (id, store_id, message, timestamp, resolved)
                   VALUES (?, ?, ?, ?, ?)"""
        await self._execute(query, (alert.id, alert.store_id, alert.message, alert.timestamp, alert.resolved))
        return alert

    async def get_alerts(self, store_id: Optional[str] = None, resolved: Optional[bool] = None) -> List[Alert]:
        query = "SELECT * FROM Alerts WHERE 1=1"
        params = []
        if store_id:
            query += " AND store_id = ?"
            params.append(store_id)
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(resolved)
        query += " ORDER BY timestamp DESC"
        rows = await self._fetchall(query, tuple(params))
        return [Alert(**row) for row in rows]

    async def resolve_alert(self, alert_id: str):
        query = "UPDATE Alerts SET resolved = 1 WHERE id = ?"
        await self._execute(query, (alert_id,))

    # Review operations
    async def save_review(self, review: Review) -> Review:
        query = """INSERT INTO Reviews (id, store_id, text, created_at)
                   VALUES (?, ?, ?, ?)"""
        await self._execute(query, (review.id, review.store_id, review.text, review.created_at))
        return review

    async def get_reviews(self, store_id: Optional[str] = None) -> List[Review]:
        query = "SELECT * FROM Reviews"
        params = ()
        if store_id:
            query += " WHERE store_id = ? ORDER BY created_at DESC"
            params = (store_id,)
        rows = await self._fetchall(query, params)
        return [Review(**row) for row in rows]

    # Report operations
    async def save_report(self, report: ExecutiveReport) -> ExecutiveReport:
        query = """INSERT INTO Reports (id, store_id, content, created_at)
                   VALUES (?, ?, ?, ?)"""
        await self._execute(query, (report.id, report.store_id, report.content, report.created_at))
        return report

    async def get_reports(self, store_id: Optional[str] = None) -> List[ExecutiveReport]:
        query = "SELECT * FROM Reports"
        params = ()
        if store_id:
            query += " WHERE store_id = ? ORDER BY created_at DESC"
            params = (store_id,)
        rows = await self._fetchall(query, params)
        return [ExecutiveReport(**row) for row in rows]

# Global database instance
db = Database()
