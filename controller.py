# -*- coding: utf-8 -*-
from logger import logger
from bs4 import BeautifulSoup
import requests
from serivce import services
from datetime import datetime
from dotenv import load_dotenv
import os, random
import asyncio
import multiprocessing

# Load environment variables
load_dotenv()

# Initialize service instance
agentService = services()

# --- Moved outside class: Safe for multiprocessing ---
def getDataFromArticles(url: str):
    """Scrape and return all paragraph text from a webpage."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        paras = soup.find_all('p')

        # Extract text from paragraphs and clean
        contentFromWebPages = [p.text for p in paras if p.text.strip() != '']
        logger.info(f"Extracted content from {url}")
        return contentFromWebPages
    except Exception as e:
        logger.error(f"Error extracting data from article {url}: {e}")
        return []

# --- Controller class ---
class agentController:
    """Controller for handling user queries and online interactions."""
    
    async def queryAnalyser(self, query: str):
        """Analyze the query and enhance it based on its intent."""
        try:
            logger.info("Analyzing query")

            # Correct spelling first
            query = await agentService.spellCorrector(query)
            print(query)

            return query
        except Exception as e:
            logger.error(f"Error during query analysis: {e}")
            return query  # Return original query if error occurs

    async def getSearchFromOnline(self, query: dict):
        """Fetch search results online, extract data, and rank based on similarity."""
        try:
            Query = query.get('query', '').strip()
            if not Query:
                return {"status_code": 400, "content in url": "Empty query provided"}

            logger.info("Starting online search")

            # Analyze the query
            processed_query = await self.queryAnalyser(Query)

            # Perform web search
            results = await agentService.getWebSearchData(processed_query)

            if not results:
                return {"status_code": 404, "content in url": "No search results found"}

            urls = []
            for r in results:
                url = r.get('href')
                if url:
                    # Check if allowed to scrape
                    is_allowed = await agentService.checkIsAllowedToScrap(
                        url=url,
                        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"
                    )
                    if is_allowed:
                        urls.append(url)
                    else:
                        logger.info(f"Not allowed to scrape: {url}")

            if not urls:
                return {"status_code": 404, "content in url": "No allowed URLs to scrape."}

            logger.info(f"Found {len(urls)} allowed URLs. Starting multiprocessing scrape...")

            # 🚀 Multiprocessing block
            loop = asyncio.get_running_loop()
            dataFromAllPages = await loop.run_in_executor(
                None,
                self.scrape_multiple_articles,
                urls
            )

            dataFromOnline = {}
            highestScore = 0

            for url, contentFromWebPage in zip(urls, dataFromAllPages):
                if not contentFromWebPage:
                    continue

                similarityScore = await agentService.checkSimilarity(context=contentFromWebPage, query=Query)

                if similarityScore > 0.5:
                    highestScore = max(highestScore, similarityScore)
                    dataFromOnline[similarityScore] = {
                        'url': url,
                        'content in url': ",".join(contentFromWebPage)
                    }

            if not dataFromOnline:
                return {"status_code": 404, "content in url": "No relevant results found on internet too, can you please ask the question in a different way :)"}
            
            summarizedText = ""
            no_sent=0
            for sentence in dataFromOnline.get(highestScore,{})['content in url'].split(". "):
                similarityScore = await agentService.checkSimilarity(context=sentence, query=Query)
                if similarityScore>0.5 and no_sent <=5:
                    summarizedText += str(sentence)+". "
                    no_sent+=1

            return {'url':dataFromOnline[highestScore]['url'],'content in url':summarizedText}

        except Exception as e:
            logger.error(f"Error during online search: {e}")
            return {"status_code": 500, "error": str(e)}

    def scrape_multiple_articles(self, urls):
        """Helper to scrape multiple articles using multiprocessing."""
        with multiprocessing.Pool(processes=min(8, len(urls))) as pool:
            results = pool.map(getDataFromArticles, urls)
        return results
