import json
import os
from datetime import datetime
from typing import List

from aiohttp import ClientSession

from bot.models.icp_metric import ICPMetric


async def fetch_and_store_metrics() -> List[int]:
    url = os.getenv("ICP_METRICS_URL")
    if not url:
        raise ValueError(f"Environment variable ICP_METRICS_URL is not set.")

    async with ClientSession() as session:
        raw_text = await _get_text(session, url)

    lines = [line for line in raw_text.splitlines() if line.strip()]
    metrics = []
    for line in lines:
        parsed = json.loads(line)
        ts_iso = datetime.fromisoformat(parsed["timestamp"])
        metrics.append(ICPMetric(data=parsed, timestamp=ts_iso))

    inserted_ids = await ICPMetric.save_many(metrics)

    async with ClientSession() as session:
        await _delete(session, url)

    return inserted_ids

async def _get_text(session: ClientSession, url: str) -> str:
    async with session.get(url, timeout=15, headers={'Authorization': os.getenv("ICP_METRICS_TOKEN")}) as resp:
        resp.raise_for_status()
        return await resp.text()


async def _delete(session: ClientSession, url: str) -> None:
    async with session.delete(url, timeout=15, headers={'Authorization': os.getenv("ICP_METRICS_TOKEN")}) as resp:
        resp.raise_for_status()


if __name__ == "__main__":
    from asyncio import run
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    run(fetch_and_store_metrics())
