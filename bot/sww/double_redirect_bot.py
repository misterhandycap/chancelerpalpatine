from typing import Dict, Iterator
from pywikibot import config, Page, showDiff
from pywikibot.exceptions import IsNotRedirectPageError, NoPageError

from bot.sww.wiki_bot import WikiBot
from bot.utils import run_blocking_io_task


class DoubleRedirectBot(WikiBot):
    def __init__(self) -> None:
        config.put_throttle = 1
        super().__init__()
        
    @run_blocking_io_task
    def get_double_redirects(self) -> Iterator[Page]:
        return self.site.double_redirects()
    
    @run_blocking_io_task
    def fix_double_redirect(self, page: Page) -> Dict[str, Page]:
        try:
            target_page: Page = page.getRedirectTarget().getRedirectTarget()
        except (IsNotRedirectPageError, NoPageError):
            raise Exception("Redirect chain contains either non redirect page or non existent page")
        page.text = f'#{self.site.redirect()} [[{target_page.title()}]]'
        return {'target_page': target_page, 'redirect_page': page}
    
    @run_blocking_io_task
    def save_page(self, page: Page) -> Page:
        if not self.site.logged_in():
            raise Exception("Bot not logged in")
        page.save('Correção de redirecionamento duplo')
        return page
        

if __name__ == '__main__':
    from asyncio import run
    
    from dotenv import load_dotenv
    
    async def main():
        double_redirect_bot = DoubleRedirectBot()
        await double_redirect_bot.get_site()
        double_redirects = await double_redirect_bot.get_double_redirects()
        await double_redirect_bot.login()
        for page in double_redirects:
            redirect_fix = await double_redirect_bot.fix_double_redirect(page)
            print(f'Redirected {page.title()} to {redirect_fix["target_page"].title()}')
            await double_redirect_bot.save_page(redirect_fix['redirect_page'])
    
    load_dotenv()
    
    run(main())
