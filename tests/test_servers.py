import asyncio
from unittest import TestCase

from dotenv import load_dotenv

from bot.models.server_config import ServerConfig
from bot.servers import cache
from bot.servers.servers import Servers
from tests.factories.server_config_factory import ServerConfigFactory
from tests.support.db_connection import clear_data, Session


class TestServers(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def setUp(self):
        self.test_session = Session()
        cache.server_configs = {}
    
    def tearDown(self):
        clear_data(self.test_session)
        self.test_session.close()
    
    def test_load_configs(self):
        server_config_1 = ServerConfigFactory(language='en')
        server_config_2 = ServerConfigFactory(language='jp')
        server_config_3 = ServerConfigFactory(language='pt')
        self.test_session.commit()

        self.assertEqual(cache.server_configs, {})

        result = asyncio.run(cache.load_configs())

        self.assertIsNone(result)
        self.assertIn(server_config_1.id, cache.server_configs)
        self.assertIn(server_config_2.id, cache.server_configs)
        self.assertIn(server_config_3.id, cache.server_configs)

        self.assertEqual(cache.server_configs.get(server_config_1.id).id, server_config_1.id)
        self.assertEqual(cache.server_configs.get(server_config_2.id).id, server_config_2.id)
        self.assertEqual(cache.server_configs.get(server_config_3.id).id, server_config_3.id)

    def test_get_config_server_config_exists(self):
        server_config_1 = ServerConfigFactory()
        cache.server_configs = {
            server_config_1.id: server_config_1
        }

        result = cache.get_config(server_config_1.id)

        self.assertEqual(result, server_config_1)

    def test_get_config_server_config_does_not_exist(self):
        result = cache.get_config(10)

        self.assertIsNone(result)

    def test_update_config_creates_new_server_config(self):
        server_id = 14
        server_language = 'pt'
        result = asyncio.run(cache.update_config(server_id, language=server_language))

        self.assertIsInstance(result, ServerConfig)
        self.assertEqual(result.id, server_id)
        self.assertEqual(result.language, server_language)
        
        fetched_server_config = self.test_session.query(ServerConfig).first()
        self.assertEqual(fetched_server_config.id, server_id)
        self.assertEqual(fetched_server_config.language, server_language)

    def test_update_config_updates_existing_server_config(self):
        server_config = ServerConfigFactory(language='en')
        self.test_session.commit()

        new_server_language = 'pt'
        result = asyncio.run(cache.update_config(server_config.id, language=new_server_language))
        Session.remove()

        self.assertIsInstance(result, ServerConfig)
        self.assertEqual(result.id, server_config.id)
        self.assertEqual(result.language, new_server_language)
        
        fetched_server_config = self.test_session.query(ServerConfig).get(server_config.id)
        self.assertEqual(fetched_server_config.id, server_config.id)
        self.assertEqual(fetched_server_config.language, new_server_language)
