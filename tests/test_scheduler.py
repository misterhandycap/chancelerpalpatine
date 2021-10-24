import asyncio
import pickle
from datetime import datetime, timedelta
from unittest import TestCase

from sqlalchemy import table
from tzlocal import get_localzone

from bot.misc.scheduler import Scheduler
from bot.models import Base
from tests.support.db_connection import clear_data, Session


class TestScheduler(TestCase):

    def setUp(self):
        self.db_session = Session()
        self.scheduler_bot = Scheduler()
    
    def tearDown(self):
        self.scheduler_bot._scheduler.remove_all_jobs()
        clear_data(self.db_session)
        self.db_session.close()

    def test_add_job(self):
        my_func = TestScheduler.schedule_func
        job_datetime = timedelta(seconds=2) + datetime.now(tz=get_localzone())

        job = self.scheduler_bot.add_job(job_datetime.strftime('%Y/%m/%d %H:%M'), my_func)

        scheduled_jobs = self.scheduler_bot._scheduler.get_jobs()
        
        self.assertEqual(len(scheduled_jobs), 1)
        self.assertEqual(scheduled_jobs[0].func, my_func)
        self.assertLessEqual(scheduled_jobs[0].trigger.run_date, job_datetime, timedelta(seconds=1))

        jobs_table = self.scheduler_bot._scheduler._jobstores['default'].jobs_t

        self.assertEqual(self.db_session.query(jobs_table).count(), 1)

    @classmethod
    def schedule_func():
        pass
