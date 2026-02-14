import asyncio
import logging
import os
import warnings
from datetime import datetime

from dotenv import load_dotenv
from vcr_unittest import VCRTestCase

from bot.models.icp_metric import ICPMetric
from bot.sww.icp_metric_fetcher import fetch_and_store_metrics
from tests.support.db_connection import clear_data, Session


class TestICPMetricFetcher(VCRTestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        warnings.simplefilter("ignore")
        logging.disable(logging.WARNING)
    
    def tearDown(self):
        clear_data(Session())
        
    def _get_vcr(self, **kwargs):
        return super()._get_vcr(cassette_library_dir=os.path.join('tests', 'support'), **kwargs)
        
    def test_fetch_and_store_metrics_success(self):
        result = asyncio.run(fetch_and_store_metrics())
        
        self.assertEqual(len(result), 1)
        
        icp_metrics = list(Session().query(ICPMetric))
        self.assertEqual(len(icp_metrics), 1)
        self.assertEqual(icp_metrics[0].id, result[0])
        self.assertEqual(icp_metrics[0].timestamp, datetime(2026, 2, 14, 19, 32, 30))
        self.assertEqual(icp_metrics[0].data, {'data': '213213', 'timestamp': '2026-02-14T19:32:30+00:00'})
        self.assertEqual(len(self.cassette.requests), 2)
        self.assertEqual(self.cassette.requests[0].method, 'GET')
        self.assertEqual(self.cassette.requests[1].method, 'DELETE')
