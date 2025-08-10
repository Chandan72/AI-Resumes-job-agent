import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "news_curation.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create articles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT UNIQUE NOT NULL,
                        source TEXT NOT NULL,
                        published_date TEXT NOT NULL,
                        content TEXT,
                        industry TEXT,
                        confidence_score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create industry_stats table for caching
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS industry_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        industry TEXT UNIQUE NOT NULL,
                        article_count INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create execution_logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS execution_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        articles_scraped INTEGER DEFAULT 0,
                        articles_classified INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'success',
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def insert_article(self, title: str, url: str, source: str, published_date: str, 
                      content: str = None, industry: str = None, confidence_score: float = None) -> bool:
        """Insert a new article into the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO articles 
                    (title, url, source, published_date, content, industry, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (title, url, source, published_date, content, industry, confidence_score))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting article: {e}")
            return False
    
    def get_articles_by_industry(self, industry: str, limit: int = 5) -> List[Dict]:
        """Get articles for a specific industry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title, url, source, published_date, confidence_score
                    FROM articles 
                    WHERE industry = ? 
                    ORDER BY published_date DESC 
                    LIMIT ?
                ''', (industry, limit))
                
                articles = []
                for row in cursor.fetchall():
                    articles.append(dict(row))
                return articles
        except Exception as e:
            logger.error(f"Error getting articles by industry: {e}")
            return []
    
    def get_articles_last_24h(self) -> List[Dict]:
        """Get all articles from the last 24 hours"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get articles from last 24 hours
                yesterday = datetime.now() - timedelta(days=1)
                cursor.execute('''
                    SELECT * FROM articles 
                    WHERE published_date >= ? 
                    ORDER BY published_date DESC
                ''', (yesterday.strftime('%Y-%m-%d'),))
                
                articles = []
                for row in cursor.fetchall():
                    articles.append(dict(row))
                return articles
        except Exception as e:
            logger.error(f"Error getting articles from last 24h: {e}")
            return []
    
    def update_article_industry(self, url: str, industry: str, confidence_score: float) -> bool:
        """Update the industry classification for an article"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE articles 
                    SET industry = ?, confidence_score = ?
                    WHERE url = ?
                ''', (industry, confidence_score, url))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating article industry: {e}")
            return False
    
    def get_industry_stats(self) -> Dict[str, int]:
        """Get article count for each industry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT industry, COUNT(*) as count
                    FROM articles 
                    WHERE industry IS NOT NULL
                    GROUP BY industry
                ''')
                
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = row[1]
                return stats
        except Exception as e:
            logger.error(f"Error getting industry stats: {e}")
            return {}
    
    def log_execution(self, articles_scraped: int, articles_classified: int, 
                     status: str = 'success', error_message: str = None) -> bool:
        """Log execution details"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO execution_logs 
                    (articles_scraped, articles_classified, status, error_message)
                    VALUES (?, ?, ?, ?)
                ''', (articles_scraped, articles_classified, status, error_message))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging execution: {e}")
            return False
    
    def cleanup_old_articles(self, days: int = 7) -> int:
        """Remove articles older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=days)
                cursor.execute('''
                    DELETE FROM articles 
                    WHERE published_date < ?
                ''', (cutoff_date.strftime('%Y-%m-%d'),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old articles")
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old articles: {e}")
            return 0