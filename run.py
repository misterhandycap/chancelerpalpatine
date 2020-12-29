import os

from dotenv import load_dotenv

from bot import client

load_dotenv()

client.run(os.environ.get("API_KEY"))