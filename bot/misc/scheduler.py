from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from bot.models import db_url


class Scheduler():
    
    def __init__(self):
        self._scheduler = AsyncIOScheduler(
            jobstores={'default': SQLAlchemyJobStore(url=db_url)}
        )
        self._scheduler.start()

    def add_job(self, dt: str, send_msg_func, args=None):
        parsed_df = datetime.strptime(dt, '%Y/%m/%d %H:%M')
        return self._scheduler.add_job(
            send_msg_func, 'date',
            run_date=parsed_df,
            args=args,
            misfire_grace_time=None
        )
