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
        self.event_loop = asyncio.new_event_loop()
        self.scheduler_bot = Scheduler(event_loop=self.event_loop)
        self.scheduler_bot.start()
    
    def tearDown(self):
        try:
            self.event_loop.close()
        except RuntimeError:
            pass
        self.scheduler_bot._scheduler.remove_all_jobs()
        clear_data(self.db_session)
        self.db_session.close()

    def test_add_job(self):
        my_func = TestScheduler.schedule_func
        job_datetime = timedelta(seconds=2) + datetime.now(tz=get_localzone())
        self.scheduler_bot.register_function('my_func', my_func)

        job = self.scheduler_bot.add_job(job_datetime, 'my_func')

        scheduled_jobs = self.scheduler_bot._scheduler.get_jobs()
        
        self.assertEqual(len(scheduled_jobs), 1)
        self.assertEqual(asyncio.run(scheduled_jobs[0].func(self.scheduler_bot, 'my_func')), asyncio.run(my_func()))
        self.assertLessEqual(scheduled_jobs[0].trigger.run_date, job_datetime)

        jobs_table = self.scheduler_bot._scheduler._jobstores['default'].jobs_t

        self.assertEqual(self.db_session.query(jobs_table).count(), 1)

    def test_parse_schedule_time_seconds(self):
        tests = ['5s', '5 s', ' 5 s', '05 seconds']
        
        for test in tests:
            result = self.scheduler_bot.parse_schedule_time(test)

            self.assertGreaterEqual(result, datetime.now() + timedelta(seconds=4))
            self.assertLessEqual(result, datetime.now() + timedelta(seconds=5))

    def test_parse_schedule_time_minutes(self):
        tests = ['5m', '5 m', ' 5 m', '05 minutes']
        
        for test in tests:
            result = self.scheduler_bot.parse_schedule_time(test)

            self.assertGreaterEqual(result, datetime.now() + timedelta(minutes=4))
            self.assertLessEqual(result, datetime.now() + timedelta(minutes=5))

    def test_parse_schedule_time_hours(self):
        tests = ['5h', '5 h', ' 5 h', '05 hours']
        
        for test in tests:
            result = self.scheduler_bot.parse_schedule_time(test)

            self.assertGreaterEqual(result, datetime.now() + timedelta(hours=4))
            self.assertLessEqual(result, datetime.now() + timedelta(hours=5))

    def test_parse_schedule_time_days(self):
        tests = ['5d', '5 d', ' 5 d', '05 days']
        
        for test in tests:
            result = self.scheduler_bot.parse_schedule_time(test)

            self.assertGreaterEqual(result, datetime.now() + timedelta(days=4))
            self.assertLessEqual(result, datetime.now() + timedelta(days=5))

    @classmethod
    async def schedule_func(*args):
        return 14
