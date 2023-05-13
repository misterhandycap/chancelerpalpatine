import re
from datetime import datetime, timedelta
from typing import Dict, Literal, Union

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from bot.models import db_url
from bot.servers import cache


class Scheduler():
    
    def __init__(self, event_loop=None):
        self._scheduler = AsyncIOScheduler(
            jobstores={'default': SQLAlchemyJobStore(url=db_url)},
            event_loop=event_loop
        )

    def start(self):
        self._scheduler.start()

    def register_function(self, name: str, func):
        cache.scheduler_functions[name] = func

    def add_date_job(self, dt: datetime, func_name: str, args=()):
        return self._scheduler.add_job(
            self._run_job, 'date',
            run_date=dt,
            args=(func_name,) + args,
            misfire_grace_time=None
        )
        
    def add_periodical_job(self, type: Literal["interval", "cron"],
                           interval: Dict[str, Union[int, str]], func_name: str,
                           args=(), *, job_id: str = None):
        try:
            return self._scheduler.add_job(
                self._run_job, type,
                **interval,
                args=(func_name,) + args,
                misfire_grace_time=None,
                id=job_id
            )
        except ConflictingIdError:
            return self._scheduler.get_job(job_id)

    async def _run_job(self, func_name, *args):
        return await cache.scheduler_functions[func_name](*args)

    def parse_schedule_time(self, text: str, timezone: str='America/Sao_Paulo') -> datetime:
        unit_dict = {
            's': 'seconds',
            'm': 'minutes',
            'h': 'hours',
            'd': 'days'
        }
        text_match = re.match(r'^(\d+)\s*([dhms])', text.strip())
        if text_match:
            num = text_match.group(1)
            unit = text_match.group(2)
            timedelta_kwargs = {unit_dict[unit]: int(num)}

            return datetime.now() + timedelta(**timedelta_kwargs)

        try:
            brt = pytz.timezone(timezone)
            return brt.localize(datetime.strptime(text, '%Y/%m/%d %H:%M'))
        except:
            return None

    def __getstate__(self):
        pickleable_dict = self.__dict__.copy()
        if '_scheduler' in pickleable_dict:
            pickleable_dict.pop('_scheduler')
        return pickleable_dict
