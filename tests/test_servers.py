import asyncio
from unittest import TestCase

from dotenv import load_dotenv

from bot.models.server_config import ServerConfig
from bot.servers import cache
from bot.servers.servers import Servers
from tests.factories.server_config_factory import ServerConfigFactory
from tests.factories.server_config_autoreply_factory import ServerConfigAutoreplyFactory
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
        server_config_3.autoreply_configs = [ServerConfigAutoreplyFactory()]
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

        server_config_3_autoreply_config = cache.server_configs.get(server_config_3.id).autoreply_configs
        self.assertEqual(len(server_config_3_autoreply_config), 1)
        self.assertEqual(server_config_3_autoreply_config[0].server_config_id, server_config_3.id)

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
        self.assertEqual(result.autoreply_configs, [])
        
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

    def test_get_autoreply_to_message_message_starts_with(self):
        server_config = ServerConfigFactory()
        server_config_autoreply_starts_with = ServerConfigAutoreplyFactory(
            message_regex='^hello')
        server_config_autoreply_ends_with = ServerConfigAutoreplyFactory(
            message_regex='.*bye$')
        server_config_autoreply_has = ServerConfigAutoreplyFactory(
            message_regex='.*wait.*')
        server_config.autoreply_configs = [
            server_config_autoreply_starts_with,
            server_config_autoreply_ends_with,
            server_config_autoreply_has
        ]
        cache.server_configs = {
            server_config.id: server_config
        }

        result = cache.get_autoreply_to_message(server_config.id, 'hello there')

        self.assertIsNotNone(result)
        self.assertEqual(result.id, server_config_autoreply_starts_with.id)

    def test_get_autoreply_to_message_message_ends_with(self):
        server_config = ServerConfigFactory()
        server_config_autoreply_starts_with = ServerConfigAutoreplyFactory(
            message_regex='^hello')
        server_config_autoreply_ends_with = ServerConfigAutoreplyFactory(
            message_regex='.*bye$')
        server_config_autoreply_has = ServerConfigAutoreplyFactory(
            message_regex='.*wait.*')
        server_config.autoreply_configs = [
            server_config_autoreply_starts_with,
            server_config_autoreply_ends_with,
            server_config_autoreply_has
        ]
        cache.server_configs = {
            server_config.id: server_config
        }

        result = cache.get_autoreply_to_message(server_config.id, 'ok, bye')

        self.assertIsNotNone(result)
        self.assertEqual(result.id, server_config_autoreply_ends_with.id)

    def test_get_autoreply_to_message_message_has(self):
        server_config = ServerConfigFactory()
        server_config_autoreply_starts_with = ServerConfigAutoreplyFactory(
            message_regex='^hello')
        server_config_autoreply_ends_with = ServerConfigAutoreplyFactory(
            message_regex='.*bye$')
        server_config_autoreply_has = ServerConfigAutoreplyFactory(
            message_regex='.*wait.*')
        server_config.autoreply_configs = [
            server_config_autoreply_starts_with,
            server_config_autoreply_ends_with,
            server_config_autoreply_has
        ]
        cache.server_configs = {
            server_config.id: server_config
        }

        result = cache.get_autoreply_to_message(server_config.id, 'please, wait for me')

        self.assertIsNotNone(result)
        self.assertEqual(result.id, server_config_autoreply_has.id)

    def test_get_autoreply_to_message_no_match(self):
        server_config = ServerConfigFactory()
        server_config_autoreply_starts_with = ServerConfigAutoreplyFactory(
            message_regex='^hello')
        server_config_autoreply_ends_with = ServerConfigAutoreplyFactory(
            message_regex='.*bye$')
        server_config_autoreply_has = ServerConfigAutoreplyFactory(
            message_regex='.*wait.*')
        server_config.autoreply_configs = [
            server_config_autoreply_starts_with,
            server_config_autoreply_ends_with,
            server_config_autoreply_has
        ]
        cache.server_configs = {
            server_config.id: server_config
        }

        result = cache.get_autoreply_to_message(server_config.id, 'nopee')

        self.assertIsNone(result)

    def test_get_reply(self):
        server_config = ServerConfigFactory()
        server_config_autoreply = ServerConfigAutoreplyFactory(
            message_regex='tão sábi(\\w) (.*)', reply='Já ouviu a história de Darth \\2, \\1 sábi\\1?')
        server_config.autoreply_configs = [
            server_config_autoreply
        ]
        message = 'Tão sábia Lele'
        
        result = server_config_autoreply.get_reply(message)
        
        self.assertEqual(result, 'Já ouviu a história de Darth Lele, a sábia?')
