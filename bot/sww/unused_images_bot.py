from typing import Iterator, Tuple

from pywikibot import config, FilePage

from bot.sww.wiki_bot import WikiBot
from bot.utils import run_blocking_io_task


class UnusedImagesBot(WikiBot):
    def __init__(self) -> None:
        config.put_throttle = 1
        super().__init__()
    
    @run_blocking_io_task
    def get_unused_images(self) -> Iterator[FilePage]:
        return self.site.unusedfiles()
    
    @run_blocking_io_task
    def check_for_deletion(self, file_page: FilePage) -> Tuple[bool, str]:
        if not file_page.exists():
            return False, "Page does not exist"
        if list(file_page.categories()):
            return False, "Image has categories"
        
        return True, ""
    
    @run_blocking_io_task
    def delete_image(self, file_page: FilePage) -> FilePage:
        return file_page.delete(reason="Imagem não utilizada", prompt=False, mark=False)


if __name__ == "__main__":
    from asyncio import run
    
    from dotenv import load_dotenv
    
    async def main():
        unused_images_bot = UnusedImagesBot()
        await unused_images_bot.get_site()
        images = await unused_images_bot.get_unused_images()
        await unused_images_bot.login()
        for image in images:
            should_delete, reason = await unused_images_bot.check_for_deletion(image)
            if should_delete:
                await unused_images_bot.delete_image(image)
                print(f"Deleted image {image.title()}")
            else:
                print(f"Could not delete image {image.title()}: {reason}")
    
    load_dotenv()
    
    run(main())
