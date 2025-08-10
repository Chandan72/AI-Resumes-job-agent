import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Industry keywords for better filtering
        self.industry_keywords = {
            'Building Materials Sector': ['cement', 'steel', 'construction materials', 'building materials'],
            'Media & Entertainment': ['media', 'entertainment', 'film', 'tv', 'streaming', 'content'],
            'Paper and Pulp Manufacturing': ['paper', 'pulp', 'manufacturing', 'packaging'],
            'Consumer Electronics': ['electronics', 'smartphone', 'laptop', 'gadgets', 'consumer tech'],
            'Construction/Infrastructure': ['construction', 'infrastructure', 'roads', 'bridges', 'real estate'],
            'Battery Manufacturing': ['battery', 'lithium', 'energy storage', 'ev battery'],
            'Mining and Minerals': ['mining', 'minerals', 'coal', 'iron ore', 'bauxite'],
            'Ship Building': ['ship', 'shipping', 'maritime', 'vessel', 'shipyard'],
            'Cement': ['cement', 'concrete', 'construction materials'],
            'Pharmaceutical': ['pharma', 'medicine', 'drugs', 'healthcare', 'biotech'],
            'MSW Management': ['waste', 'management', 'recycling', 'environmental'],
            'NBFC': ['nbfc', 'finance', 'lending', 'credit', 'financial services'],
            'Healthcare': ['healthcare', 'medical', 'hospital', 'health', 'medicine'],
            'Aluminium': ['aluminium', 'aluminum', 'metal', 'manufacturing'],
            'Paint': ['paint', 'coating', 'chemicals', 'manufacturing'],
            'Telecommunications': ['telecom', 'communication', '5g', 'internet', 'mobile'],
            'Oil and Gas': ['oil', 'gas', 'petroleum', 'energy', 'fuel'],
            'Renewable Energy': ['renewable', 'solar', 'wind', 'green energy', 'clean energy'],
            'Explosives': ['explosives', 'defense', 'military', 'ammunition'],
            'Financial Services': ['finance', 'banking', 'investment', 'insurance', 'wealth'],
            'Automobiles': ['automobile', 'car', 'vehicle', 'auto', 'motor'],
            'Textiles': ['textile', 'fabric', 'clothing', 'apparel', 'garment'],
            'Travel and Tourism': ['travel', 'tourism', 'hotel', 'airline', 'vacation'],
            'Auto Ancillaries': ['auto parts', 'ancillaries', 'components', 'suppliers'],
            'Recruitment and Human Resources Services': ['hr', 'recruitment', 'hiring', 'employment', 'jobs'],
            'Power/Transmission & Equipment': ['power', 'transmission', 'electricity', 'grid', 'energy'],
            'Real Estate & Construction Software': ['real estate', 'construction software', 'proptech', 'construction tech'],
            'Electronic Manufacturing Services': ['ems', 'electronics manufacturing', 'contract manufacturing'],
            'Fast Moving Consumer Goods': ['fmcg', 'consumer goods', 'retail', 'fast moving'],
            'Contract Development and Manufacturing Organisation': ['cdmo', 'contract manufacturing', 'pharma manufacturing'],
            'Fashion & Apparels': ['fashion', 'apparel', 'clothing', 'style', 'design'],
            'Aviation': ['aviation', 'airline', 'aircraft', 'aerospace', 'flight']
        }
    
    def scrape_economic_times(self) -> List[Dict]:
        """Scrape news from Economic Times"""
        articles = []
        try:
            url = "https://economictimes.indiatimes.com"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article links
            article_links = soup.find_all('a', href=True)
            
            for link in article_links:
                href = link.get('href')
                if href and '/news/' in href and not href.startswith('http'):
                    full_url = urljoin(url, href)
                    
                    # Get article title
                    title_elem = link.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        # Check if article is from last 24 hours
                        if self._is_recent_article(full_url):
                            articles.append({
                                'title': title,
                                'url': full_url,
                                'source': 'Economic Times',
                                'published_date': datetime.now().strftime('%Y-%m-%d'),
                                'content': self._extract_article_content(full_url)
                            })
                            
                            if len(articles) >= 20:  # Limit articles per source
                                break
                                
        except Exception as e:
            logger.error(f"Error scraping Economic Times: {e}")
            
        return articles
    
    def scrape_business_standard(self) -> List[Dict]:
        """Scrape news from Business Standard"""
        articles = []
        try:
            url = "https://www.business-standard.com"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article links
            article_links = soup.find_all('a', href=True)
            
            for link in article_links:
                href = link.get('href')
                if href and '/article/' in href and not href.startswith('http'):
                    full_url = urljoin(url, href)
                    
                    # Get article title
                    title_elem = link.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        # Check if article is from last 24 hours
                        if self._is_recent_article(full_url):
                            articles.append({
                                'title': title,
                                'url': full_url,
                                'source': 'Business Standard',
                                'published_date': datetime.now().strftime('%Y-%m-%d'),
                                'content': self._extract_article_content(full_url)
                            })
                            
                            if len(articles) >= 20:  # Limit articles per source
                                break
                                
        except Exception as e:
            logger.error(f"Error scraping Business Standard: {e}")
            
        return articles
    
    def scrape_mint(self) -> List[Dict]:
        """Scrape news from Mint"""
        articles = []
        try:
            url = "https://www.livemint.com"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article links
            article_links = soup.find_all('a', href=True)
            
            for link in article_links:
                href = link.get('href')
                if href and '/news/' in href and not href.startswith('http'):
                    full_url = urljoin(url, href)
                    
                    # Get article title
                    title_elem = link.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        # Check if article is from last 24 hours
                        if self._is_recent_article(full_url):
                            articles.append({
                                'title': title,
                                'url': full_url,
                                'source': 'Mint',
                                'published_date': datetime.now().strftime('%Y-%m-%d'),
                                'content': self._extract_article_content(full_url)
                            })
                            
                            if len(articles) >= 20:  # Limit articles per source
                                break
                                
        except Exception as e:
            logger.error(f"Error scraping Mint: {e}")
            
        return articles
    
    def _extract_article_content(self, url: str) -> str:
        """Extract article content from a given URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content
            content_selectors = [
                'article',
                '.article-content',
                '.story-content',
                '.content',
                'main',
                '.main-content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            # If no specific content found, get body text
            if not content:
                content = soup.get_text(strip=True)
            
            # Limit content length
            return content[:2000] if len(content) > 2000 else content
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""
    
    def _is_recent_article(self, url: str) -> bool:
        """Check if article is from last 24 hours (basic check)"""
        # For now, we'll assume all articles are recent
        # In a production system, you'd parse actual publication dates
        return True
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all news sources and return combined articles"""
        all_articles = []
        
        logger.info("Starting news scraping from all sources...")
        
        # Scrape each source
        sources = [
            ('Economic Times', self.scrape_economic_times),
            ('Business Standard', self.scrape_business_standard),
            ('Mint', self.scrape_mint)
        ]
        
        for source_name, scraper_func in sources:
            try:
                logger.info(f"Scraping {source_name}...")
                articles = scraper_func()
                all_articles.extend(articles)
                logger.info(f"Scraped {len(articles)} articles from {source_name}")
                
                # Add delay between sources to be respectful
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to scrape {source_name}: {e}")
        
        # Remove duplicates based on URL
        unique_articles = self._remove_duplicates(all_articles)
        logger.info(f"Total unique articles scraped: {len(unique_articles)}")
        
        return unique_articles
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles
    
    def get_industry_suggestions(self, title: str, content: str) -> List[str]:
        """Get industry suggestions based on keywords in title and content"""
        suggestions = []
        text = (title + " " + content).lower()
        
        for industry, keywords in self.industry_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    suggestions.append(industry)
                    break
        
        return suggestions[:3]  # Return top 3 suggestions