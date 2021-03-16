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
