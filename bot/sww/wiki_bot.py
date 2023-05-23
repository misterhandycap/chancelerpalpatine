import logging
import os

from pywikibot import APISite
from pywikibot.login import ClientLoginManager, BotPassword

from bot.sww.sww_family import StarWarsWikiFamily
from bot.utils import run_blocking_io_task


class WikiBot():
    def __init__(self) -> None:
        self.site: APISite = None
    
    @run_blocking_io_task
    def get_site(self) -> APISite:
        self.site = APISite(fam=StarWarsWikiFamily(), code='pt', user=os.environ.get("SWW_BOT_USERNAME"))
        return self.site
    
    @run_blocking_io_task
    def login(self) -> None:
        logging.getLogger('pywiki').disabled = True
        try:
            bot_password = BotPassword(
                os.environ.get("SWW_BOT_USERNAME"), os.environ.get('SWW_BOT_PASSWORD'))
            login_manager = ClientLoginManager(site=self.site, user=self.site.username())
            login_manager.password = bot_password.password
            login_manager.login_name = bot_password.login_name(login_manager.username)
            login_manager.login()
        except:
            logging.getLogger('pywiki').disabled = False
            raise
        finally:
            logging.getLogger('pywiki').disabled = False
        self.site._username = login_manager.username
        del self.site.userinfo
        self.site.userinfo
    
