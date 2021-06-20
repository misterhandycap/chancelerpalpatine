from unittest import TestCase

from bot.models.server_config_autoreply import ServerConfigAutoreply


class TestServerConfigAutoreply(TestCase):

    def test_get_reply_replace(self):
        server_config_autoreply = ServerConfigAutoreply(message_regex='\\breplace me\\b', reply='replaced')

        result = server_config_autoreply.get_reply('please replace me!')

        self.assertEqual(result, 'please replaced!')

    def test_get_reply_multiline(self):
        server_config_autoreply = ServerConfigAutoreply(message_regex='\\breplace me.*', reply='replaced')

        result = server_config_autoreply.get_reply('please replace me!\nMe too')

        self.assertEqual(result, 'please replaced')
