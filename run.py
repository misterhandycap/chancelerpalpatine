import os

from dotenv import load_dotenv

from bot import client
from bot.astrology_cmds import *
from bot.bot import *
from bot.level import *
from bot.sww_cmds import *

load_dotenv()

client.run(os.environ.get("API_KEY"))
