AI News Curation Agent

Stack: FastAPI (Python), aiohttp + BeautifulSoup (RSS scraping), OpenAI GPT for classification, SQLite, React (Vite), APScheduler, Docker.

Features
- Scrapes last 24h articles from Economic Times, Business Standard, Mint (via RSS)
- Classifies into 32 industries using OpenAI with confidence scores
- Deduplicates by URL
- Dashboard shows 32 industry cards with counts and top 5 articles
- Runs daily at 10:00 AM IST automatically; manual trigger endpoint

Quick Start
1. Create `.env` from `.env.example` and fill `OPENAI_API_KEY`.
2. Build and run with Docker Compose:
   - `docker compose up --build`
3. Open frontend: http://localhost:5173

API
- GET /health
- GET /industries
- GET /articles?industry=&limit=&offset=
- GET /last_updated
- POST /trigger  # manual run

Notes
- Scheduler timezone is `Asia/Kolkata`. Change via `TIMEZONE` env.
- SQLite stored at `data/news.db` volume.
- To run backend locally: `uvicorn backend.main:app --reload` from project root with virtualenv.