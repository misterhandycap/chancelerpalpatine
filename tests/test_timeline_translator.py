import json
import os
from asyncio import run

from pywikibot import BaseSite, Page, Site, config

from bot.sww.sww_family import StarWarsWikiFamily
from bot.sww.timeline_translator import TimelineTranslator
from tests.support.pywikibot_test_case import PywikibotTestCase


class TestTimelineTranslator(PywikibotTestCase):
    
    @PywikibotTestCase.skip_if_no_bot_config
    def test_login(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = self.get_test_site()
        
        run(timeline_translator.login())
        
        self.assertTrue(timeline_translator.site.logged_in())
    
    def test_get_wookiee_page(self):
        timeline_translator = TimelineTranslator(auto_close_session=True)

        result = run(timeline_translator.get_wookiee_page())

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIsNotNone(timeline_translator._original_content)
        
    def test_get_timeline_page(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = self.get_test_site()
        
        result = run(timeline_translator.get_timeline_page())
        
        self.assertIsInstance(timeline_translator.site, BaseSite)
        self.assertEqual(result, timeline_translator.page)
        self.assertIsInstance(result, Page)
        self.assertEqual(result.title(), "Linha do tempo de mídia canônica")
        self.assertIsInstance(timeline_translator._current_content, str)
        self.assertGreater(len(timeline_translator._current_content), 0)
        self.assertEqual(timeline_translator._current_content, result.text)
        self.assertEqual(timeline_translator._current_revision, result.latest_revision_id)
        
    def test_build_new_references_with_new_messages(self):
        timeline_translator = TimelineTranslator()
        
        with open(os.path.join('tests', 'support', 'canon_media_timeline_sww.txt')) as f:
            timeline_translator._current_content = f.read()
        with open(os.path.join('tests', 'support', 'canon_media_timeline_wookiee.txt')) as f:
            timeline_translator._original_content = f.read()
            
        result = timeline_translator.build_new_references()
        
        self.assertEqual(result.keys(), set([
            'Legends',
            'The High Republic: Path of Vengeance',
            'After the Fall',
            'RescueDate',
            'Lost Stars',
            'Kanan placement',
            'Kanan flashbacks',
            'DisarmingLesson',
            'SecondChance',
            'Beast Within',
            'DarkVisions',
            'B2-5ABY',
            'Hunters',
            'Resistance Reborn Date'
        ]))
    
    def test_build_new_references_without_new_messages(self):
        timeline_translator = TimelineTranslator()
        
        with open(os.path.join('tests', 'support', 'canon_media_timeline_wookiee.txt')) as f:
            timeline_translator._current_content = f.read()
        with open(os.path.join('tests', 'support', 'canon_media_timeline_wookiee.txt')) as f:
            timeline_translator._original_content = f.read()
            
        result = timeline_translator.build_new_references()
        
        self.assertEqual(result, {})
        
    def test_build_new_references_ref_without_name(self):
        timeline_translator = TimelineTranslator()
        
        timeline_translator._current_content = """
        <ref name="named">Named translated</ref>
        <ref name="959171f4040ece69390025112b6622c7">Unnamed translated</ref>
        """
        
        timeline_translator._original_content = """
        <ref name="named">Named ref</ref>
        <ref name="new_named">New named ref</ref>
        <ref>Unnamed ref</ref>
        <ref>New unnamed ref</ref>
        <ref>New unnamed ref [[2 BBY]]</ref>
        """
        
        result = timeline_translator.build_new_references()
        
        self.assertEqual(result.keys(), set([
            "new_named",
            "c8e26b64231cc9078d74595799fa5ad3",
            "2a99324bfc3351ce6d76ba04a0d1121b"
        ]))
        
    def test_add_reference_translation_new_ref(self):
        timeline_translator = TimelineTranslator()
        
        timeline_translator.add_reference_translation('ref_name', 'content')
        
        self.assertEqual(timeline_translator._translated_refs, {'ref_name': 'content'})
    
    def test_add_reference_translation_existing_key_overwrites(self):
        timeline_translator = TimelineTranslator()
        timeline_translator._translated_refs = {'ref_name': 'old_content'}
        
        timeline_translator.add_reference_translation('ref_name', 'content')
        
        self.assertEqual(timeline_translator._translated_refs, {'ref_name': 'content'})
        
    def test_translate_page_success(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = self.get_test_site()
        
        with open(os.path.join('tests', 'support', 'canon_media_timeline_sww.txt')) as f:
            timeline_translator._current_content = f.read()
        with open(os.path.join('tests', 'support', 'canon_media_timeline_wookiee.txt')) as f:
            timeline_translator._original_content = f.read()
        with open(os.path.join('tests', 'support', 'canon_media_timeline_translated_references.json')) as f:
            timeline_translator._translated_refs = json.load(f)
        timeline_translator.page = Page(timeline_translator.site, 'Star Wars Wiki:Testes')
        
        result = timeline_translator.translate_page()
        
        self.assertIsInstance(result, Page)
        self.assertEqual(result, timeline_translator.page)
        with open(os.path.join('tests', 'support', 'canon_media_timeline_translated.txt')) as f:
            self.assertEqual(result.text, f.read())

    def test_translate_page_translated_ref_name(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = self.get_test_site()
        
        timeline_translator._current_content = """
        {|
        |}
        {|
        |
        |}
        """
        timeline_translator._original_content = """
        {|
        |}
        {|
        |<ref name="Lost Stars">Some content</ref>
        |}
        """
        expected_content = """
        {|
        |}
        {|
        |<ref name="Lost Stars">translated</ref>
        |}
        """
            
        timeline_translator._translated_refs = {
            'Lost Stars': 'translated',
        }
        timeline_translator.page = Page(timeline_translator.site, 'Star Wars Wiki:Testes')
        
        result = timeline_translator.translate_page()
        
        self.assertIsInstance(result, Page)
        self.assertEqual(result, timeline_translator.page)
        self.assertEqual(result.text, expected_content)
    
    def test_translate_page_with_unnamed_references(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = self.get_test_site()
        
        timeline_translator._current_content = """
        {|
        |}
        {|
        |
        |}
        """
        timeline_translator._original_content = """
        {|
        |}
        {|
        |<ref>Some content in Lost Stars</ref>
        |}
        """
        expected_content = """
        {|
        |}
        {|
        |<ref name="8a5bec216f3ae74840db2de2e46a7408">translated</ref>
        |}
        """
            
        timeline_translator._translated_refs = {
            '8a5bec216f3ae74840db2de2e46a7408': 'translated',
        }
        timeline_translator.page = Page(timeline_translator.site, 'Star Wars Wiki:Testes')
        
        result = timeline_translator.translate_page()
        
        self.assertIsInstance(result, Page)
        self.assertEqual(result, timeline_translator.page)
        self.assertEqual(result.text, expected_content)
    
    def test_translate_page_raises_when_there_are_missing_refs(self):
        timeline_translator = TimelineTranslator()
        
        with open(os.path.join('tests', 'support', 'canon_media_timeline_sww.txt')) as f:
            timeline_translator._current_content = f.read()
        with open(os.path.join('tests', 'support', 'canon_media_timeline_wookiee.txt')) as f:
            timeline_translator._original_content = f.read()
        
        with self.assertRaises(Exception):
            timeline_translator.translate_page()
            
    @PywikibotTestCase.skip_if_no_bot_config
    def test_save_page_success(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = self.get_test_site()
        config.put_throttle = 0
        timeline_translator.page = Page(timeline_translator.site, 'Star Wars Wiki:Testes')
        
        run(timeline_translator.save_page())
    
    def test_save_page_raises_when_not_logged_in(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = Site(
            fam=StarWarsWikiFamily(), 
            code='pt', 
            user='invalid_user'
        )
        timeline_translator.page = Page(timeline_translator.site, 'Star Wars Wiki:Testes')
        
        with self.assertRaises(Exception):
            run(timeline_translator.save_page())
    
    def test_get_diff_url(self):
        timeline_translator = TimelineTranslator()
        timeline_translator.site = self.get_test_site()
        timeline_translator.page = Page(timeline_translator.site, 'Linha do tempo de mídia canônica')
        timeline_translator._current_revision = timeline_translator.page.latest_revision_id
        
        result = timeline_translator.get_diff_url()
        
        self.assertIn("https://", result)
        self.assertIn(str(timeline_translator._current_revision), result)
        self.assertIn("diff=next", result)
