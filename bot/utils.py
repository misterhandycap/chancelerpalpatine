import subprocess
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, Tuple, TypeVar

from asyncio import get_running_loop, new_event_loop
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

from bot.chess.player import Player

try:
    current_bot_version = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
except:
    current_bot_version = None

PR = ParamSpec('PR')
RT = TypeVar('RT')

def run_blocking_io_task(func: Callable[PR, RT], *args, **kwargs) -> Callable[PR, Awaitable[RT]]:
    async def function_wrapper(*args: PR.args, **kwargs: PR.kwargs) -> Coroutine[Any, Any, RT]:
        loop = get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))
    return function_wrapper

def run_cpu_bound_task(func, *args, **kwargs):
    async def function_wrapper(*args, **kwargs):
        loop = get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, partial(func, *args, **kwargs))
    return function_wrapper

def run_cpu_bound_task_with_event_loop(func, *args, **kwargs):
    def function_wrapper(*args, **kwargs):
        event_loop = new_event_loop()
        try:
            corofn = func(*args, **kwargs)
            return event_loop.run_until_complete(corofn)
        finally:
            event_loop.close()
    return function_wrapper

def convert_users_to_players(*args):
        return tuple(map(lambda user: Player(user) if user else None, args))
    
def paginate(elems: list, page: int, itens_per_page: int) -> Tuple[list, int]:
    """
    Paginates long list into pages and returns requested page

    Pages indexes start at 1.

    :param elems: Elements to be paginated
    :type elems: list
    :param page: Page number to be returned
    :type page: int
    :param itens_per_page: Max number of elements per page
    :type itens_per_page: int
    :return: Paginated list and last page
    :rtype: Tuple[list, int]
    """
    len_elems = len(elems)
    last_page = len_elems // itens_per_page + (len_elems % itens_per_page > 0)
    page = min(max(page, 1), last_page)
    interval_start = (page-1) * itens_per_page
    interval_end = page * itens_per_page
    return elems[interval_start:interval_end], last_page
