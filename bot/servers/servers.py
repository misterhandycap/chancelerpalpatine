import re

from bot.models.server_config import ServerConfig


class Servers():

    def __init__(self):
        self.server_configs = {}
        self.all_servers = []

    async def load_configs(self):
        all_server_configs = await ServerConfig.all()
        self.server_configs = {sc.id: sc for sc in all_server_configs}

    def get_config(self, server_id):
        return self.server_configs.get(server_id)

    async def update_config(self, server_id, **kwargs):
        server_config = await ServerConfig.get(server_id) or ServerConfig(id=server_id)
        for key, value in kwargs.items():
            setattr(server_config, key, value)
        await ServerConfig.save(server_config)
        self.server_configs[server_id] = server_config
        return server_config

    def get_autoreply_to_message(self, server_id, message: str):
        server_config = self.get_config(server_id)
        if not server_config or not server_config.autoreply_configs:
            return
        for autoreply_config in server_config.autoreply_configs:
            if re.match(autoreply_config.message_regex, message):
                return autoreply_config
