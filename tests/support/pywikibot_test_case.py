import logging
import shutil
import os
import warnings

from dotenv import load_dotenv
from pywikibot import config, APISite
from unittest import skip
from vcr_unittest import VCRTestCase

from bot.sww.sww_family import StarWarsWikiFamily


class PywikibotTestCase(VCRTestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        warnings.simplefilter("ignore")
        logging.disable(logging.WARNING)
        config.put_throttle = 0
        super().setUpClass()
        
    def setUp(self):
        open('throttle.ctrl', 'w').close()
        shutil.rmtree('apicache-py3', ignore_errors=True)
        os.mkdir('apicache-py3')
        super().setUp()
        
    @staticmethod
    def skip_if_no_bot_config(func):
        def wrapper(*args, **kwargs):
            if os.environ.get('SWW_BOT_PASSWORD') is None:
                return skip("No SWW bot configured")
            return func(*args, **kwargs)
        return wrapper
    
    def get_test_site(self) -> APISite:
        return APISite(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user=os.environ.get("SWW_BOT_USERNAME")
        )
