from __future__ import annotations

import os
import asyncio
import datetime as dt
import logging
from typing import Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .database import SessionLocal, upsert_meta, insert_articles
from .scraper import fetch_latest_articles
from .classifier import classify_article

logger = logging.getLogger("news.scheduler")

scheduler = BackgroundScheduler()

IST = pytz.timezone(os.getenv("TIMEZONE", "Asia/Kolkata"))


async def _run_curation_once() -> Dict[str, Any]:
    logger.info("Starting curation run (last 24h)...")
    try:
        articles = await fetch_latest_articles(hours=24)
    except Exception as e:
        logger.exception("Failed to fetch latest articles: %s", e)
        articles = []

    logger.info("Fetched %d candidate articles", len(articles))

    classified = []
    for a in articles:
        try:
            cls = classify_article(a["title"], a.get("summary"))
            a["industry"] = cls.get("industry")
            a["confidence"] = cls.get("confidence")
            classified.append(a)
        except Exception:
            logger.exception("Classification failed for url=%s", a.get("url"))

    db = SessionLocal()
    try:
        inserted = insert_articles(db, classified)
        upsert_meta(db, "last_updated", dt.datetime.now(dt.timezone.utc).isoformat())
        logger.info("Inserted %d new articles", inserted)
    except Exception:
        logger.exception("DB insert/upsert failed")
        inserted = 0
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
            logger.info("Scheduled job started")
            result = asyncio.run(_run_curation_once())
            logger.info("Scheduled job completed: %s", result)
        except Exception:
            logger.exception("Scheduled job failed")

    scheduler.add_job(job_wrapper, trigger, id="daily_curation", replace_existing=True)
    scheduler.start()

    # Optional immediate run on startup
    run_now = os.getenv("RUN_ON_STARTUP", "true").lower() in {"1", "true", "yes"}
    if run_now:
        try:
            logger.info("RUN_ON_STARTUP=true -> running one curation immediately")
            job_wrapper()
        except Exception:
            logger.exception("Immediate run on startup failed")