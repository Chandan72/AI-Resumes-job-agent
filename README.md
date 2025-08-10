# AI News Curation Agent

A complete automated news curation system that extracts articles from Economic Times, Business Standard, and Mint, classifies them by industry using AI, and displays them on a beautiful dashboard. The system runs automatically every morning at 10 AM IST.

## 🚀 Features

- **Automated News Scraping**: Extracts articles from 3 major Indian business news sources
- **AI-Powered Classification**: Uses OpenAI GPT-4 to classify articles into 32 industry categories
- **Smart Scheduling**: Automatically runs daily at 10 AM IST using APScheduler
- **Real-time Dashboard**: Beautiful React.js dashboard showing industry-wise news
- **Article Deduplication**: Prevents duplicate articles from being stored
- **Confidence Scoring**: AI classification includes confidence scores for reliability
- **Manual Trigger**: Option to manually trigger news curation
- **Error Handling**: Comprehensive error handling and logging
- **Docker Ready**: Easy deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   News Sources  │    │   FastAPI       │    │   React.js      │
│                 │    │   Backend       │    │   Frontend      │
│ • Economic      │───▶│                 │◀──▶│                 │
│   Times        │    │ • Scraper       │    │ • Dashboard     │
│ • Business     │    │ • Classifier    │    │ • Industry      │
│   Standard     │    │ • Scheduler     │    │   Cards         │
│ • Mint         │    │ • Database      │    │ • Controls      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SQLite        │
                       │   Database      │
                       │                 │
                       │ • Articles      │
                       │ • Classifications│
                       │ • Execution Logs│
                       └─────────────────┘
```

## 🎯 Industry Categories (32 Total)

1. Building Materials Sector
2. Media & Entertainment
3. Paper and Pulp Manufacturing
4. Consumer Electronics
5. Construction/Infrastructure
6. Battery Manufacturing
7. Mining and Minerals
8. Ship Building
9. Cement
10. Pharmaceutical
11. MSW Management
12. NBFC
13. Healthcare
14. Aluminium
15. Paint
16. Telecommunications
17. Oil and Gas
18. Renewable Energy
19. Explosives
20. Financial Services
21. Automobiles
22. Textiles
23. Travel and Tourism
24. Auto Ancillaries
25. Recruitment and Human Resources Services
26. Power/Transmission & Equipment
27. Real Estate & Construction Software
28. Electronic Manufacturing Services
29. Fast Moving Consumer Goods
30. Contract Development and Manufacturing Organisation
31. Fashion & Apparels
32. Aviation

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLite
- **Web Scraping**: BeautifulSoup4, Requests, aiohttp
- **AI Classification**: OpenAI GPT-4 API
- **Scheduling**: APScheduler with timezone support
- **Frontend**: React.js 18, Tailwind CSS
- **Containerization**: Docker, Docker Compose
- **Database**: SQLite (with automatic cleanup)

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional)
- OpenAI API key

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-news-agent
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

1. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure environment**
   ```bash
   # Copy and edit .env.example in the backend directory
   cp .env.example .env
   # Add your OpenAI API key
   ```

4. **Start the services**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Database Configuration
DATABASE_URL=sqlite:///./news_curation.db

# News Sources
ECONOMIC_TIMES_URL=https://economictimes.indiatimes.com
BUSINESS_STANDARD_URL=https://www.business-standard.com
MINT_URL=https://www.livemint.com

# Scheduler Configuration
SCHEDULER_TIMEZONE=Asia/Kolkata
SCHEDULER_HOUR=10
SCHEDULER_MINUTE=0

# Logging
LOG_LEVEL=INFO
```

### Customizing Schedule

To change the daily execution time, modify the environment variables:

```env
SCHEDULER_HOUR=9    # 9 AM
SCHEDULER_MINUTE=30 # 30 minutes past the hour
```

## 📊 API Endpoints

### Core Endpoints

- `GET /` - System information
- `GET /health` - Health check
- `GET /stats` - System statistics
- `POST /curate` - Manually trigger news curation

### Articles & Industries

- `GET /articles` - Get articles with optional filtering
- `GET /industries` - Get industry statistics and articles

### Scheduler Control

- `GET /scheduler/status` - Get scheduler status
- `POST /scheduler/start` - Start the scheduler
- `POST /scheduler/stop` - Stop the scheduler
- `POST /scheduler/trigger` - Manually trigger execution

## 🎛️ Dashboard Features

### Control Panel
- **Scheduler Control**: Start/stop automatic daily execution
- **Manual Trigger**: Run news curation on demand
- **System Status**: Real-time monitoring of all components

### Industry Dashboard
- **32 Industry Cards**: Each showing article count and recent articles
- **Article Links**: Direct links to source articles
- **Confidence Scores**: AI classification confidence indicators
- **Auto-refresh**: Updates every 5 minutes

### System Statistics
- Total articles in last 24 hours
- Industries with articles
- Next scheduled execution
- Scheduler status

## 🔄 How It Works

1. **Daily Schedule**: At 10 AM IST, the scheduler automatically triggers news curation
2. **News Scraping**: Articles are extracted from Economic Times, Business Standard, and Mint
3. **Content Extraction**: Article titles, content, and metadata are extracted
4. **AI Classification**: OpenAI GPT-4 classifies each article into one of 32 industries
5. **Database Storage**: Articles and classifications are stored in SQLite database
6. **Dashboard Update**: Frontend displays industry-wise news with real-time updates
7. **Cleanup**: Old articles (older than 7 days) are automatically removed

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is correctly set in `.env`
   - Check if you have sufficient API credits

2. **Scraping Failures**
   - News websites may change their structure
   - Check logs for specific error messages
   - Consider implementing rate limiting

3. **Scheduler Not Running**
   - Check timezone configuration
   - Verify scheduler status in dashboard
   - Check logs for initialization errors

4. **Database Issues**
   - Ensure write permissions in the data directory
   - Check if SQLite database is accessible

### Logs

Check the logs for detailed error information:

```bash
# Docker logs
docker-compose logs backend

# Local logs (if running locally)
# Check console output and any log files
```

## 🔧 Development

### Project Structure

```
ai-news-agent/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── scraper.py        # News scraping logic
│   ├── classifier.py     # AI classification
│   ├── database.py       # Database operations
│   ├── scheduler.py      # Task scheduling
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile       # Backend container
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json      # Node.js dependencies
│   └── Dockerfile       # Frontend container
├── docker-compose.yml    # Service orchestration
├── .env.example         # Environment template
└── README.md            # This file
```

### Adding New News Sources

1. Add scraping logic in `backend/scraper.py`
2. Update the `scrape_all_sources()` method
3. Test with the new source
4. Update documentation

### Modifying Industry Categories

1. Update the industries list in `backend/classifier.py`
2. Modify industry descriptions if needed
3. Retrain or test with existing articles
4. Update frontend industry list

## 📈 Performance & Scaling

### Current Limitations

- Single-threaded scraping (can be improved with async)
- SQLite database (suitable for small to medium scale)
- Single instance deployment

### Scaling Considerations

- Use PostgreSQL for larger datasets
- Implement Redis for caching
- Add load balancing for multiple instances
- Use message queues for background processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 API
- FastAPI for the excellent web framework
- React.js team for the frontend framework
- BeautifulSoup for web scraping capabilities

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub
4. Check the API documentation at `/docs` when running

---

**Note**: This system is designed for educational and research purposes. Please ensure compliance with the terms of service of the news sources and OpenAI API usage policies.
