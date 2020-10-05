from asyncio import get_running_loop
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

from bot.chess.player import Player

def run_cpu_bound_task(func, *args, **kwargs):
    async def function_wrapper(*args, **kwargs):
        loop = get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, partial(func, *args, **kwargs))
    return function_wrapper

def convert_users_to_players(*args):
        return tuple(map(lambda user: Player(user) if user else None, args))
