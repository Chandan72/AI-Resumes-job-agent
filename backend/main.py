import logging
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import asyncio

# Import our modules
from database import DatabaseManager
from scraper import NewsScraper
from classifier import NewsClassifier
from scheduler import NewsCurationScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI News Curation Agent",
    description="Automated news curation system with AI-powered industry classification",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseManager()
scraper = NewsScraper()
classifier = None  # Will be initialized when API key is available
scheduler = None  # Will be initialized after setup

# Pydantic models
class ArticleResponse(BaseModel):
    title: str
    url: str
    source: str
    published_date: str
    industry: Optional[str] = None
    confidence_score: Optional[float] = None

class IndustryStatsResponse(BaseModel):
    industry: str
    article_count: int
    average_confidence: float
    articles: List[ArticleResponse]

class CurationResponse(BaseModel):
    success: bool
    message: str
    articles_scraped: int
    articles_classified: int
    execution_time: float

class SchedulerStatusResponse(BaseModel):
    is_running: bool
    next_execution: Optional[str]
    timezone: str
    schedule_time: str
    total_jobs: int

# Global variables
curation_in_progress = False

def initialize_classifier():
    """Initialize the classifier if API key is available"""
    global classifier
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            classifier = NewsClassifier(api_key)
            logger.info("News classifier initialized successfully")
            return True
        else:
            logger.warning("OpenAI API key not configured. AI classification will be disabled.")
            return False
    except Exception as e:
        logger.error(f"Error initializing classifier: {e}")
        return False

def initialize_scheduler():
    """Initialize the scheduler"""
    global scheduler
    try:
        scheduler = NewsCurationScheduler(curation_workflow)
        logger.info("News curation scheduler initialized")
        return True
    except Exception as e:
        logger.error(f"Error initializing scheduler: {e}")
        return False

def curation_workflow() -> Dict:
    """
    Main news curation workflow
    
    Returns:
        Dict with execution results
    """
    global curation_in_progress
    
    if curation_in_progress:
        logger.warning("Curation already in progress, skipping...")
        return {"status": "skipped", "reason": "Already in progress"}
    
    curation_in_progress = True
    start_time = datetime.now()
    
    try:
        logger.info("Starting news curation workflow...")
        
        # Step 1: Scrape news from all sources
        logger.info("Step 1: Scraping news articles...")
        articles = scraper.scrape_all_sources()
        articles_scraped = len(articles)
        logger.info(f"Scraped {articles_scraped} articles")
        
        # Step 2: Store articles in database
        logger.info("Step 2: Storing articles in database...")
        articles_stored = 0
        for article in articles:
            if db.insert_article(
                title=article['title'],
                url=article['url'],
                source=article['source'],
                published_date=article['published_date'],
                content=article.get('content', '')
            ):
                articles_stored += 1
        
        logger.info(f"Stored {articles_stored} articles in database")
        
        # Step 3: Classify articles if classifier is available
        articles_classified = 0
        if classifier:
            logger.info("Step 3: Classifying articles with AI...")
            classified_articles = classifier.classify_multiple_articles(articles)
            
            # Update database with classifications
            for article in classified_articles:
                if db.update_article_industry(
                    article['url'],
                    article['industry'],
                    article['confidence_score']
                ):
                    articles_classified += 1
            
            logger.info(f"Classified {articles_classified} articles")
        else:
            logger.info("Step 3: Skipping AI classification (classifier not available)")
        
        # Step 4: Log execution
        execution_time = (datetime.now() - start_time).total_seconds()
        db.log_execution(
            articles_scraped=articles_scraped,
            articles_classified=articles_classified,
            status='success'
        )
        
        # Step 5: Cleanup old articles
        db.cleanup_old_articles(days=7)
        
        result = {
            "status": "success",
            "articles_scraped": articles_scraped,
            "articles_stored": articles_stored,
            "articles_classified": articles_classified,
            "execution_time": execution_time
        }
        
        logger.info(f"News curation workflow completed successfully: {result}")
        return result
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        error_msg = str(e)
        
        logger.error(f"Error in news curation workflow: {error_msg}")
        
        # Log failed execution
        db.log_execution(
            articles_scraped=0,
            articles_classified=0,
            status='error',
            error_message=error_msg
        )
        
        return {
            "status": "error",
            "error": error_msg,
            "execution_time": execution_time
        }
    
    finally:
        curation_in_progress = False

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info("Starting AI News Curation Agent...")
    
    # Initialize classifier
    initialize_classifier()
    
    # Initialize scheduler
    if initialize_scheduler():
        try:
            scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI News Curation Agent...")
    
    if scheduler:
        scheduler.stop()

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI News Curation Agent API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "classifier": "available" if classifier else "unavailable",
        "scheduler": "running" if scheduler and scheduler.is_running else "stopped"
    }

@app.post("/curate", response_model=CurationResponse)
async def trigger_curation(background_tasks: BackgroundTasks):
    """Manually trigger news curation"""
    if curation_in_progress:
        raise HTTPException(status_code=409, detail="Curation already in progress")
    
    # Run curation in background
    background_tasks.add_task(curation_workflow)
    
    return CurationResponse(
        success=True,
        message="News curation started in background",
        articles_scraped=0,
        articles_classified=0,
        execution_time=0.0
    )

@app.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    industry: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50
):
    """Get articles with optional filtering"""
    try:
        if industry:
            articles = db.get_articles_by_industry(industry, limit)
        else:
            articles = db.get_articles_last_24h()
            if source:
                articles = [a for a in articles if a['source'] == source]
            articles = articles[:limit]
        
        return articles
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving articles")

@app.get("/industries", response_model=List[IndustryStatsResponse])
async def get_industry_stats():
    """Get statistics for all industries"""
    try:
        stats = db.get_industry_stats()
        
        # Get articles for each industry
        industry_stats = []
        for industry, count in stats.items():
            articles = db.get_articles_by_industry(industry, 5)
            avg_confidence = 0.0
            
            if articles:
                confidences = [a.get('confidence_score', 0) for a in articles]
                avg_confidence = sum(confidences) / len(confidences)
            
            industry_stats.append(IndustryStatsResponse(
                industry=industry,
                article_count=count,
                average_confidence=round(avg_confidence, 3),
                articles=articles
            ))
        
        # Sort by article count (descending)
        industry_stats.sort(key=lambda x: x.article_count, reverse=True)
        
        return industry_stats
    except Exception as e:
        logger.error(f"Error getting industry stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving industry statistics")

@app.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    """Get scheduler status"""
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not available")
    
    return scheduler.get_scheduler_status()

@app.post("/scheduler/start")
async def start_scheduler():
    """Start the scheduler"""
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not available")
    
    try:
        scheduler.start()
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting scheduler: {e}")

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler"""
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not available")
    
    try:
        scheduler.stop()
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping scheduler: {e}")

@app.post("/scheduler/trigger")
async def trigger_scheduler():
    """Manually trigger the scheduler"""
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not available")
    
    try:
        success = scheduler.trigger_manual_execution()
        if success:
            return {"message": "Manual execution triggered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Manual execution failed")
    except Exception as e:
        logger.error(f"Error triggering manual execution: {e}")
        raise HTTPException(status_code=500, detail=f"Error triggering execution: {e}")

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        # Get basic stats
        total_articles = len(db.get_articles_last_24h())
        industry_stats = db.get_industry_stats()
        
        # Calculate total articles by industry
        total_by_industry = sum(industry_stats.values())
        
        # Get scheduler status
        scheduler_status = scheduler.get_scheduler_status() if scheduler else {"is_running": False}
        
        return {
            "total_articles_24h": total_articles,
            "total_articles_by_industry": total_by_industry,
            "industries_with_articles": len([c for c in industry_stats.values() if c > 0]),
            "scheduler_running": scheduler_status.get("is_running", False),
            "next_execution": scheduler_status.get("next_execution"),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving system statistics")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )