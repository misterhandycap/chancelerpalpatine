import re
from uuid import uuid4

from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from bot.models import Base
from bot.models.guid import GUID


class ServerConfigAutoreply(Base):
    __tablename__ = 'server_config_autoreply'
    id = Column(GUID, primary_key=True, default=uuid4)
    server_config_id = Column(BigInteger, ForeignKey('server_config.id'), nullable=False)
    message_regex = Column(String, nullable=False)
    reply = Column(String, nullable=True)
    reaction = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    def get_reply(self, message):
        case_insensitive_pattern = re.compile(self.message_regex, re.I | re.DOTALL)
        return re.sub(case_insensitive_pattern, self.reply, message)
