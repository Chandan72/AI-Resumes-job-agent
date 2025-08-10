from __future__ import annotations

import os
import asyncio
import datetime as dt
from typing import Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .database import SessionLocal, upsert_meta, insert_articles
from .scraper import fetch_latest_articles
from .classifier import classify_article

scheduler = BackgroundScheduler()

IST = pytz.timezone(os.getenv("TIMEZONE", "Asia/Kolkata"))


async def _run_curation_once() -> Dict[str, Any]:
    articles = await fetch_latest_articles(hours=24)

    classified = []
    for a in articles:
        cls = classify_article(a["title"], a.get("summary"))
        a["industry"] = cls.get("industry")
        a["confidence"] = cls.get("confidence")
        classified.append(a)

    db = SessionLocal()
    try:
        inserted = insert_articles(db, classified)
        upsert_meta(db, "last_updated", dt.datetime.now(dt.timezone.utc).isoformat())
    finally:
        db.close()
    return {"fetched": len(articles), "inserted": inserted}


def run_curation_blocking() -> Dict[str, Any]:
    return asyncio.run(_run_curation_once())


def start_scheduler() -> None:
    # Run daily at 10:00 IST
    trigger = CronTrigger(hour=10, minute=0, timezone=IST)

    def job_wrapper():
        try:
            asyncio.run(_run_curation_once())
        except Exception:
            pass

    scheduler.add_job(job_wrapper, trigger, id="daily_curation", replace_existing=True)
    scheduler.start()