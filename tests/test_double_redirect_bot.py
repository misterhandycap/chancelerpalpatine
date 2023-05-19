import logging
import os
import shutil
import warnings
from asyncio import run
from unittest import skip

from dotenv import load_dotenv
from pywikibot import APISite, Page, config
from vcr_unittest import VCRTestCase

from bot.sww.double_redirect_bot import DoubleRedirectBot
from bot.sww.sww_family import StarWarsWikiFamily


class TestDoubleRedirectBot(VCRTestCase):
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
    
    def test_get_double_redirects(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = APISite(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user=os.environ.get("SWW_BOT_USERNAME")
        )
        
        result = run(double_redirect_bot.get_double_redirects())
        
        self.assertTrue(all([p.isRedirectPage() for p in result]))
    
    def test_fix_double_redirect_success(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = APISite(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user=os.environ.get("SWW_BOT_USERNAME")
        )
        redirect_page = Page(double_redirect_bot.site, "Star Wars Wiki:Testes")
        intermediary_page = Page(double_redirect_bot.site, "User:BB-08")
        target_page = Page(double_redirect_bot.site, "Página principal")
        redirect_page._isredir = True
        redirect_page._redirtarget = intermediary_page
        intermediary_page._isredir = True
        intermediary_page._redirtarget = target_page
        
        result = run(double_redirect_bot.fix_double_redirect(redirect_page))
        
        self.assertIn('redirect_page', result)
        self.assertIn('target_page', result)
        self.assertIsInstance(result['redirect_page'], Page)
        self.assertIsInstance(result['target_page'], Page)
        self.assertEqual(result['redirect_page'].text, '#REDIRECIONAMENTO [[Página principal]]')
    
    def test_fix_double_redirect_raises_when_page_is_not_redirect(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = APISite(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user=os.environ.get("SWW_BOT_USERNAME")
        )
        page = Page(double_redirect_bot.site, "Star Wars Wiki:Testes")
        
        with self.assertRaises(Exception, msg="Redirect chain contains either non redirect page or non existent page"):
            run(double_redirect_bot.fix_double_redirect(page))
    
    def test_fix_double_redirect_raises_when_intermediate_page_does_not_exist(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = APISite(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user=os.environ.get("SWW_BOT_USERNAME")
        )
        page = Page(double_redirect_bot.site, "Star Wars Wiki:Testes")
        page._isredir = True
        page._redirtarget = Page(double_redirect_bot.site, "Inexistent")
        
        with self.assertRaises(Exception, msg="Redirect chain contains either non redirect page or non existent page"):
            run(double_redirect_bot.fix_double_redirect(page))
            
    @skip_if_no_bot_config
    def test_save_page_success(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = APISite(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user=os.environ.get("SWW_BOT_USERNAME")
        )
        page = Page(double_redirect_bot.site, "Star Wars Wiki:Testes")
        config.put_throttle = 0
        run(double_redirect_bot.login())
        
        run(double_redirect_bot.save_page(page))
    
    def test_save_page_raises_when_not_logged_in(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = APISite(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user='invalid'
        )
        page = Page(double_redirect_bot.site, "Star Wars Wiki:Testes")
        
        with self.assertRaises(Exception):
            run(double_redirect_bot.save_page(page))
