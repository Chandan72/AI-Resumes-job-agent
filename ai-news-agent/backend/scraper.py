from __future__ import annotations

import asyncio
import datetime as dt
from typing import List, Dict, Any
from email.utils import parsedate_to_datetime

import aiohttp
from bs4 import BeautifulSoup

RSS_SOURCES = [
    {
        "name": "Economic Times",
        "source": "economictimes",
        "url": "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    },
    {
        "name": "Business Standard",
        "source": "businessstandard",
        "url": "https://www.business-standard.com/rss/latest.rss",
    },
    {
        "name": "Mint",
        "source": "mint",
        "url": "https://www.livemint.com/rss/news",
    },
]


async def _fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        resp.raise_for_status()
        # Some feeds send xml with different encodings; force utf-8 fallback
        text = await resp.text(errors="ignore")
        return text


def _parse_rss(xml_text: str, source_key: str, source_name: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(xml_text, "xml")
    items = soup.find_all("item")
    articles: List[Dict[str, Any]] = []
    for it in items:
        title = (it.title.text if it.title else "").strip()
        link = (it.link.text if it.link else "").strip()
        desc = (it.description.text if it.description else None)
        pub = None
        if it.pubDate:
            try:
                pub = parsedate_to_datetime(it.pubDate.text)
            except Exception:
                pub = None
        articles.append({
            "title": title,
            "url": link,
            "summary": BeautifulSoup(desc or "", "html.parser").get_text().strip() or None,
            "published_at": pub,
            "source": source_key,
            "source_name": source_name,
        })
    return articles


def _within_last_hours(dt_value: dt.datetime | None, hours: int) -> bool:
    if not dt_value:
        return False
    if not dt_value.tzinfo:
        dt_value = dt_value.replace(tzinfo=dt.timezone.utc)
    now = dt.datetime.now(dt.timezone.utc)
    return (now - dt_value) <= dt.timedelta(hours=hours)


async def fetch_latest_articles(hours: int = 24) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    headers = {
        "User-Agent": "ai-news-agent/1.0 (+https://example.com)"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        texts = await asyncio.gather(*[_fetch(session, s["url"]) for s in RSS_SOURCES], return_exceptions=True)
        for src, txt in zip(RSS_SOURCES, texts):
            if isinstance(txt, Exception):
                continue
            try:
                parsed = _parse_rss(txt, src["source"], src["name"])
                filtered = [a for a in parsed if _within_last_hours(a.get("published_at"), hours)]
                results.extend(filtered)
            except Exception:
                continue
    return results