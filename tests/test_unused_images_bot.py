from asyncio import run

from pywikibot import Page
from pywikibot.exceptions import NoPageError

from bot.sww.unused_images_bot import UnusedImagesBot
from tests.support.pywikibot_test_case import PywikibotTestCase


class TestUnusedImagesBot(PywikibotTestCase):
    def test_get_unused_images(self):
        unused_images_bot = UnusedImagesBot()
        unused_images_bot.site = self.get_test_site()
        
        result = run(unused_images_bot.get_unused_images())
        
        self.assertTrue(all([p.is_filepage() for p in result]))
        
    
    def test_check_for_deletion_when_image_is_ok(self):
        unused_images_bot = UnusedImagesBot()
        unused_images_bot.site = self.get_test_site()
        image = Page(unused_images_bot.site, "File:Badge-picture-2.png")
        
        result = run(unused_images_bot.check_for_deletion(image))
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0])
        self.assertEqual(result[1], "")
    
    def test_check_for_deletion_when_image_does_not_exist(self):
        unused_images_bot = UnusedImagesBot()
        unused_images_bot.site = self.get_test_site()
        image = Page(unused_images_bot.site, "File:invalid")
        
        result = run(unused_images_bot.check_for_deletion(image))
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Page does not exist")
    
    def test_check_for_deletion_when_image_has_categories(self):
        unused_images_bot = UnusedImagesBot()
        unused_images_bot.site = self.get_test_site()
        image = Page(unused_images_bot.site, "File:ICP icons.png")
        
        result = run(unused_images_bot.check_for_deletion(image))
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Image has categories")
    
    @PywikibotTestCase.skip_if_no_bot_config
    def test_delete_image(self):
        unused_images_bot = UnusedImagesBot()
        unused_images_bot.site = self.get_test_site()
        image = Page(unused_images_bot.site, "File:invalid")
        
        with self.assertRaises(NoPageError):
            run(unused_images_bot.delete_image(image))