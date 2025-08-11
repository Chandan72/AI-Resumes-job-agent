from __future__ import annotations

import os
import datetime as dt
from typing import Optional, Dict, Any

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv

from .database import init_db, get_db_session, fetch_industry_counts, fetch_recent_articles_by_industry, fetch_articles, get_meta
from .scheduler import start_scheduler, run_curation_blocking, logger as sched_logger
from .classifier import INDUSTRIES

# Load .env from project root even when running inside backend/
load_dotenv(find_dotenv())

app = FastAPI(title="AI News Curation Agent", version="1.0.0")

# CORS
frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin] if frontend_origin != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    import logging
    logging.basicConfig(level=logging.INFO)
    sched_logger.setLevel(logging.INFO)
    start_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/industries")
def get_industries(db=Depends(get_db_session)):
    counts = fetch_industry_counts(db)
    # ensure all industries present with zero
    data = []
    for ind in INDUSTRIES + ["Uncategorized"]:
        data.append({
            "industry": ind,
            "count": int(counts.get(ind, 0)),
            "articles": fetch_recent_articles_by_industry(db, None if ind == "Uncategorized" else ind, limit=5),
        })
    return {"industries": data}


@app.get("/articles")
def list_articles(industry: Optional[str] = Query(default=None), limit: int = 20, offset: int = 0, db=Depends(get_db_session)):
    items = fetch_articles(db, industry=industry, limit=limit, offset=offset)
    return {"items": items, "count": len(items)}


@app.get("/last_updated")
def last_updated(db=Depends(get_db_session)):
    ts = get_meta(db, "last_updated")
    return {"last_updated": ts}


@app.post("/trigger")
def trigger_run():
    result: Dict[str, Any] = run_curation_blocking()
    return {"status": "ok", **result}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)