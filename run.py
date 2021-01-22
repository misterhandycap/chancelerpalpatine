import os

from dotenv import load_dotenv

from bot.client import client

load_dotenv()

client.run(os.environ.get("API_KEY"))
