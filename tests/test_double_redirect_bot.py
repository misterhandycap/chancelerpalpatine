from asyncio import run

from pywikibot import APISite, Page, config

from bot.sww.double_redirect_bot import DoubleRedirectBot
from bot.sww.sww_family import StarWarsWikiFamily
from tests.support.pywikibot_test_case import PywikibotTestCase


class TestDoubleRedirectBot(PywikibotTestCase):
    def test_get_double_redirects(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = self.get_test_site()
        
        result = run(double_redirect_bot.get_double_redirects())
        
        self.assertTrue(all([p.isRedirectPage() for p in result]))
    
    def test_fix_double_redirect_success(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = self.get_test_site()
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
        double_redirect_bot.site = self.get_test_site()
        page = Page(double_redirect_bot.site, "Star Wars Wiki:Testes")
        
        with self.assertRaises(Exception, msg="Redirect chain contains either non redirect page or non existent page"):
            run(double_redirect_bot.fix_double_redirect(page))
    
    def test_fix_double_redirect_raises_when_intermediate_page_does_not_exist(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = self.get_test_site()
        page = Page(double_redirect_bot.site, "Star Wars Wiki:Testes")
        page._isredir = True
        page._redirtarget = Page(double_redirect_bot.site, "Inexistent")
        
        with self.assertRaises(Exception, msg="Redirect chain contains either non redirect page or non existent page"):
            run(double_redirect_bot.fix_double_redirect(page))
            
    @PywikibotTestCase.skip_if_no_bot_config
    def test_save_page_success(self):
        double_redirect_bot = DoubleRedirectBot()
        double_redirect_bot.site = self.get_test_site()
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
