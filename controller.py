# -*- coding: utf-8 -*-
from logger import logger
from bs4 import BeautifulSoup
import requests
from serivce import services
from datetime import datetime
from dotenv import load_dotenv
import os, random

# Load environment variables
load_dotenv()

# Initialize service instance
agentService = services()

class agentController:
    """Controller for handling user queries and online interactions."""
    
    async def queryAnalyser(self, query: str):
        """Analyze the query and enhance it based on its intent."""
        try:
            logger.info("Analyzing query")

            # Correct spelling first
            query = await agentService.spellCorrector(query)
            print(query)

            # Get query intent and keywords
            queryIntentAndKeywords = await agentService.getIntentAndKeywordsOfQuery(query)
            keywords = queryIntentAndKeywords.get('Keywords', [])

            if not keywords:
                return query  # If no keywords, return corrected query directly

            random_keyword = random.choice(keywords)
            intent = queryIntentAndKeywords.get('Intent', 'informational')

            # Modify the query based on detected intent
            if intent == "recent news":
                query += f" inurl:{random_keyword} {os.getenv('NEWS_BASE_URL_STR', '')}"
            elif intent == "trend analysis":
                query += f" inurl:{random_keyword} today's date: {datetime.now().date()}"
            elif intent == "instructional":
                query += f" inurl:{random_keyword} {os.getenv('INSTRUCTION_BASE_URL_STR', '')}"
            elif intent == "definition":
                query += f" inurl:{random_keyword}"
            elif intent == "causal explanation":
                query += f" inurl:{random_keyword} {os.getenv('CE_BASE_URL_STR', '')}"
            elif intent == "opinion":
                query += f" inurl:{random_keyword} {os.getenv('OPIN_BASE_URL_STR', '')}"
            elif intent == "commercial":
                query += f" inurl:{random_keyword} {os.getenv('COMMERCIAL_BASE_URL_STR', '')}"
            elif intent == "informational":
                query += f" inurl:{random_keyword}"

            return query
        except Exception as e:
            logger.error(f"Error during query analysis: {e}")
            return query  # Return original query if error occurs

    async def getSearchFromOnline(self, query: dict):
        """Fetch search results online, extract data, and rank based on similarity."""
        try:
            Query = query.get('query', '').strip()
            if not Query:
                return {"status_code": 400, "error": "Empty query provided"}

            logger.info("Starting online search")

            # Analyze the query
            processed_query = await self.queryAnalyser(Query)

            # Perform web search
            results = await agentService.getWebSearchData(processed_query)

            if not results:
                return {"status_code": 404, "error": "No search results found"}

            dataFromOnline = {}
            highestScore = 0

            for r in results:
                url = r.get('href')
                if not url:
                    continue

                # Check if allowed to scrape
                if await agentService.checkIsAllowedToScrap(url=url, user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"):
                    contentFromWebPage = await getDataFromArticles(url)
                    
                    if not contentFromWebPage:
                        continue
                    
                    # Check similarity
                    similarityScore = await agentService.checkSimilarity(context=contentFromWebPage, query=Query)

                    if similarityScore > 0.5:
                        highestScore = max(highestScore, similarityScore)
                        dataFromOnline[similarityScore] = {
                            'url': url,
                            'content in url': f"{r.get('body', '')} " + ",".join(contentFromWebPage)
                        }
                else:
                    logger.info(f"Not allowed to scrape: {url}")

            if not dataFromOnline:
                return {"status_code": 404, "error": "No relevant results found"}

            return dataFromOnline.get(highestScore, {})
        
        except Exception as e:
            logger.error(f"Error during online search: {e}")
            return {"status_code": 500, "error": str(e)}

async def getDataFromArticles(url: str):
    """Scrape and return all paragraph text from a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        paras = soup.find_all('p')

        # Extract text from paragraphs and clean
        contentFromWebPages = [p.get_text(strip=True) for p in paras if p.get_text(strip=True)]

        return contentFromWebPages
    except Exception as e:
        logger.error(f"Error extracting data from article {url}: {e}")
        return []

