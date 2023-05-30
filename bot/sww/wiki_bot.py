import logging
import os

from pywikibot import APISite, config
from pywikibot.login import ClientLoginManager, BotPassword

from bot.sww.sww_family import StarWarsWikiFamily
from bot.utils import run_blocking_io_task


class WikiBot():
    PASSWORD_FILE_PATH = "user-password.py"
    
    def __init__(self) -> None:
        self.site: APISite = None
        self.username: str = os.environ.get("SWW_BOT_USERNAME")
        self._password: str = os.environ.get("SWW_BOT_PASSWORD")
    
    @run_blocking_io_task
    def get_site(self) -> APISite:
        self.site = APISite(fam=StarWarsWikiFamily(), code='pt', user=self.username)
        
        with open(self.PASSWORD_FILE_PATH, 'w') as f:
            f.write(f"('{self.username}', BotPassword('{self.username}', '{self._password}'))")
        config.password_file = self.PASSWORD_FILE_PATH
        
        return self.site
    
    @run_blocking_io_task
    def login(self) -> None:
        logging.getLogger('pywiki').disabled = True
        try:
            bot_password = BotPassword(self.username, self._password)
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
    
