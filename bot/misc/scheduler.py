from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from bot.models import db_url
from bot.servers import cache


class Scheduler():
    
    def __init__(self):
        self._scheduler = AsyncIOScheduler(
            jobstores={'default': SQLAlchemyJobStore(url=db_url)}
        )

    def start(self):
        self._scheduler.start()

    def register_function(self, name: str, func):
        cache.scheduler_functions[name] = func

    def add_job(self, dt: str, func_name: str, args=()):
        parsed_df = datetime.strptime(dt, '%Y/%m/%d %H:%M')
        return self._scheduler.add_job(
            self._run_job, 'date',
            run_date=parsed_df,
            args=(func_name,) + args,
            misfire_grace_time=None
        )

    async def _run_job(self, func_name, *args):
        return await cache.scheduler_functions[func_name](*args)

    def __getstate__(self):
        pickleable_dict = self.__dict__.copy()
        pickleable_dict.pop('_scheduler')
        return pickleable_dict
