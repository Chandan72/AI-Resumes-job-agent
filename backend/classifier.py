import openai
import logging
from typing import List, Dict, Tuple
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsClassifier:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        # Define the 32 industry categories
        self.industries = [
            "Building Materials Sector",
            "Media & Entertainment",
            "Paper and Pulp Manufacturing",
            "Consumer Electronics",
            "Construction/Infrastructure",
            "Battery Manufacturing",
            "Mining and Minerals",
            "Ship Building",
            "Cement",
            "Pharmaceutical",
            "MSW Management",
            "NBFC",
            "Healthcare",
            "Aluminium",
            "Paint",
            "Telecommunications",
            "Oil and Gas",
            "Renewable Energy",
            "Explosives",
            "Financial Services",
            "Automobiles",
            "Textiles",
            "Travel and Tourism",
            "Auto Ancillaries",
            "Recruitment and Human Resources Services",
            "Power/Transmission & Equipment",
            "Real Estate & Construction Software",
            "Electronic Manufacturing Services",
            "Fast Moving Consumer Goods",
            "Contract Development and Manufacturing Organisation",
            "Fashion & Apparels",
            "Aviation"
        ]
        
        # Create industry descriptions for better classification
        self.industry_descriptions = {
            "Building Materials Sector": "Companies involved in manufacturing and supplying building materials like steel, cement, bricks, tiles, etc.",
            "Media & Entertainment": "Companies in broadcasting, film production, streaming services, publishing, and entertainment content",
            "Paper and Pulp Manufacturing": "Companies manufacturing paper, pulp, packaging materials, and related products",
            "Consumer Electronics": "Companies manufacturing and selling consumer electronic devices like smartphones, laptops, TVs, etc.",
            "Construction/Infrastructure": "Companies involved in construction projects, infrastructure development, roads, bridges, buildings",
            "Battery Manufacturing": "Companies manufacturing batteries for various applications including EVs, electronics, and energy storage",
            "Mining and Minerals": "Companies involved in mining operations, mineral extraction, and processing",
            "Ship Building": "Companies involved in shipbuilding, maritime construction, and vessel manufacturing",
            "Cement": "Companies manufacturing cement, concrete, and related construction materials",
            "Pharmaceutical": "Companies involved in drug development, manufacturing, and distribution",
            "MSW Management": "Companies involved in municipal solid waste management, recycling, and environmental services",
            "NBFC": "Non-Banking Financial Companies providing financial services like lending, investment, etc.",
            "Healthcare": "Companies providing healthcare services, medical equipment, hospitals, and medical technology",
            "Aluminium": "Companies involved in aluminium production, processing, and manufacturing",
            "Paint": "Companies manufacturing paints, coatings, and related chemical products",
            "Telecommunications": "Companies providing telecom services, internet, mobile networks, and communication infrastructure",
            "Oil and Gas": "Companies involved in oil and gas exploration, production, refining, and distribution",
            "Renewable Energy": "Companies involved in solar, wind, hydro, and other renewable energy generation",
            "Explosives": "Companies manufacturing explosives for mining, construction, and defense applications",
            "Financial Services": "Banks, insurance companies, investment firms, and other financial institutions",
            "Automobiles": "Companies manufacturing cars, motorcycles, and other motor vehicles",
            "Textiles": "Companies involved in textile manufacturing, fabric production, and garment manufacturing",
            "Travel and Tourism": "Companies in hospitality, airlines, travel agencies, and tourism services",
            "Auto Ancillaries": "Companies manufacturing auto parts, components, and accessories",
            "Recruitment and Human Resources Services": "Companies providing HR services, recruitment, staffing, and employment solutions",
            "Power/Transmission & Equipment": "Companies involved in power generation, transmission, and electrical equipment",
            "Real Estate & Construction Software": "Companies developing software for real estate, construction management, and property technology",
            "Electronic Manufacturing Services": "Companies providing contract manufacturing services for electronics",
            "Fast Moving Consumer Goods": "Companies manufacturing and selling consumer goods like food, beverages, personal care products",
            "Contract Development and Manufacturing Organisation": "Companies providing contract manufacturing and development services, especially in pharma",
            "Fashion & Apparels": "Companies in fashion design, clothing manufacturing, and retail fashion",
            "Aviation": "Companies involved in aircraft manufacturing, airline operations, and aviation services"
        }
    
    def classify_article(self, title: str, content: str, source: str) -> Tuple[str, float]:
        """
        Classify a news article into one of the 32 industry categories
        
        Returns:
            Tuple of (industry, confidence_score)
        """
        try:
            # Prepare the prompt for classification
            prompt = self._create_classification_prompt(title, content, source)
            
            # Make API call to OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial analyst specializing in industry classification. Your task is to classify news articles into specific industry categories based on their content and context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=200
            )
            
            # Parse the response
            classification_result = self._parse_classification_response(response.choices[0].message.content)
            
            return classification_result
            
        except Exception as e:
            logger.error(f"Error classifying article '{title}': {e}")
            # Return a default classification with low confidence
            return "Financial Services", 0.1
    
    def _create_classification_prompt(self, title: str, content: str, source: str) -> str:
        """Create the prompt for article classification"""
        
        # Truncate content if too long
        content_preview = content[:1000] if len(content) > 1000 else content
        
        prompt = f"""
Please classify the following news article into one of the 32 industry categories listed below.

Article Title: {title}
Article Source: {source}
Article Content Preview: {content_preview}

Available Industry Categories:
{chr(10).join([f"{i+1}. {industry}" for i, industry in enumerate(self.industries)])}

Industry Descriptions:
{chr(10).join([f"{industry}: {desc}" for industry, desc in self.industry_descriptions.items()])}

Instructions:
1. Analyze the article content carefully
2. Consider the title, source, and content context
3. Choose the most appropriate industry category
4. Provide your response in this exact format:
   Industry: [Industry Name]
   Confidence: [0.0-1.0]
   Reasoning: [Brief explanation]

Please ensure the Industry Name exactly matches one of the 32 categories listed above.
"""
        return prompt
    
    def _parse_classification_response(self, response: str) -> Tuple[str, float]:
        """Parse the classification response from OpenAI"""
        try:
            lines = response.strip().split('\n')
            industry = None
            confidence = 0.5  # Default confidence
            
            for line in lines:
                line = line.strip()
                if line.startswith('Industry:'):
                    industry = line.replace('Industry:', '').strip()
                elif line.startswith('Confidence:'):
                    try:
                        conf_str = line.replace('Confidence:', '').strip()
                        confidence = float(conf_str)
                        # Ensure confidence is between 0 and 1
                        confidence = max(0.0, min(1.0, confidence))
                    except ValueError:
                        confidence = 0.5
            
            # Validate industry
            if industry and industry in self.industries:
                return industry, confidence
            else:
                # If industry not found, try to find closest match
                closest_industry = self._find_closest_industry(industry)
                return closest_industry, confidence * 0.8  # Reduce confidence for fuzzy matches
                
        except Exception as e:
            logger.error(f"Error parsing classification response: {e}")
            return "Financial Services", 0.1
    
    def _find_closest_industry(self, industry_name: str) -> str:
        """Find the closest matching industry name"""
        if not industry_name:
            return "Financial Services"
        
        # Simple fuzzy matching
        industry_lower = industry_name.lower()
        
        for industry in self.industries:
            if industry.lower() in industry_lower or industry_lower in industry.lower():
                return industry
        
        # If no close match, return default
        return "Financial Services"
    
    def classify_multiple_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Classify multiple articles and return them with industry classifications
        
        Args:
            articles: List of article dictionaries with 'title', 'content', 'source' keys
            
        Returns:
            List of articles with added 'industry' and 'confidence_score' keys
        """
        classified_articles = []
        
        logger.info(f"Starting classification of {len(articles)} articles...")
        
        for i, article in enumerate(articles):
            try:
                logger.info(f"Classifying article {i+1}/{len(articles)}: {article['title'][:50]}...")
                
                industry, confidence = self.classify_article(
                    article['title'],
                    article.get('content', ''),
                    article['source']
                )
                
                # Add classification results
                article['industry'] = industry
                article['confidence_score'] = confidence
                
                classified_articles.append(article)
                
                # Add small delay to avoid rate limiting
                import time
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error classifying article {i+1}: {e}")
                # Add default classification
                article['industry'] = "Financial Services"
                article['confidence_score'] = 0.1
                classified_articles.append(article)
        
        logger.info(f"Completed classification of {len(classified_articles)} articles")
        return classified_articles
    
    def get_industry_statistics(self, classified_articles: List[Dict]) -> Dict[str, Dict]:
        """
        Generate statistics for each industry based on classified articles
        
        Returns:
            Dictionary with industry statistics
        """
        stats = {}
        
        for industry in self.industries:
            industry_articles = [a for a in classified_articles if a.get('industry') == industry]
            
            if industry_articles:
                avg_confidence = sum(a.get('confidence_score', 0) for a in industry_articles) / len(industry_articles)
                stats[industry] = {
                    'article_count': len(industry_articles),
                    'average_confidence': round(avg_confidence, 3),
                    'articles': industry_articles[:5]  # Top 5 articles
                }
            else:
                stats[industry] = {
                    'article_count': 0,
                    'average_confidence': 0.0,
                    'articles': []
                }
        
        return stats