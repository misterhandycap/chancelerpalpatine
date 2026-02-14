"""Model for ICPMetric.

Stores each line from a JSONL payload into a separate row.
"""

from datetime import datetime

from bot.models import Base, engine
from bot.models.guid import GUID
from sqlalchemy import Column, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4


class ICPMetric(Base):
    """Represents a single JSONL entry.

    The model stores the raw JSON string in the ``data`` column.
    A ``timestamp`` column records when the row was created.
    """

    __tablename__ = "icp_metric"

    id = Column(GUID, primary_key=True, nullable=False, default=uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    data = Column(JSON, nullable=False)

    @classmethod
    async def save_many(cls, metrics: list["ICPMetric"]):
        """Persist a list of metrics to the DB.

        Args:
            metrics: List of :class:`ICPMetric` instances that have already
                     been instantiated.
        """
        async with AsyncSession(engine) as session:
            session.add_all(metrics)
            await session.commit()
            return [m.id for m in metrics]
