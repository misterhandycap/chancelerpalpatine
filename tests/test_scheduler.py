import asyncio
import pickle
from datetime import datetime, timedelta
from unittest import TestCase

import pytz
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
        tests = ['30s', '30 s', ' 30 s', '30 seconds']
        
        for test in tests:
            result = self.scheduler_bot.parse_schedule_time(test)

            self.assertGreaterEqual(result, datetime.now() + timedelta(seconds=29))
            self.assertLessEqual(result, datetime.now() + timedelta(seconds=30))

    def test_parse_schedule_time_minutes(self):
        tests = ['30m', '30 m', ' 30 m', '30 minutes']
        
        for test in tests:
            result = self.scheduler_bot.parse_schedule_time(test)

            self.assertGreaterEqual(result, datetime.now() + timedelta(minutes=29))
            self.assertLessEqual(result, datetime.now() + timedelta(minutes=30))

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
            
    def test_parse_schedule_time_formated_datetime(self):
        test = '2021/12/31 00:00'
        timezone_name = 'America/Sao_Paulo'
        expected = pytz.timezone(timezone_name).localize(datetime(2021, 12, 31, 0, 0))
        
        result = self.scheduler_bot.parse_schedule_time(test, timezone_name)
        
        self.assertEqual(result, expected)

    @classmethod
    async def schedule_func(*args):
        return 14
