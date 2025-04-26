# -*- coding: utf-8 -*-
from logger import logger
from bs4 import BeautifulSoup
import requests
from serivce import services
from datetime import datetime
from dotenv import load_dotenv
import os,random

load_dotenv()
agentService = services()

class agentController:
    """Controller for the agent class.
    This class is responsible for handling the agent's actions and interactions with the web.
    """
    async def queryAnalyser(self,query:str):
        """Analyse the query for breakdown complex question in searchable compontents"""
        logger.info("Analyzing query")
        # Get the intent and keyword of the query by getIntentOfQuery function
        query = await agentService.spellCorrector(query)
        print(query)
        queryIntentAndKeywords = await agentService.getIntentAndKeywordsOfQuery(query)
        
        if queryIntentAndKeywords['Intent'] == "recent news" : query+=f"inurl:{random.choice(queryIntentAndKeywords['Keywords'])} {os.getenv("NEWS_BASE_URL_STR")}"
        elif queryIntentAndKeywords['Intent'] == "trend analysis" : query+=f"inurl:{random.choice(queryIntentAndKeywords['Keywords'])}  today's date : {datetime.now().date()}"
        elif queryIntentAndKeywords['Intent'] == "instructional" : query+=f"inurl:{random.choice(queryIntentAndKeywords['Keywords'])}  {os.getenv("INSTRUCTION_BASE_URL_STR")}"
        elif queryIntentAndKeywords['Intent'] == "definition" : query+=f" inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "causal explanation" : query+=f"inurl:{random.choice(queryIntentAndKeywords['Keywords'])} {os.getenv("CE_BASE_URL_STR")}"
        elif queryIntentAndKeywords['Intent'] == "opinion" : query+=f"inurl:{random.choice(queryIntentAndKeywords['Keywords'])} {os.getenv("OPIN_BASE_URL_STR")}"
        elif queryIntentAndKeywords['Intent'] == "commercial" : query+=f"inurl:{random.choice(queryIntentAndKeywords['Keywords'])}  {os.getenv("COMMERCIAL_BASE_URL_STR")}"
        elif queryIntentAndKeywords['Intent'] == "informational" : query+=f" inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        
        return query


    async def getSearchFromOnline(self,query:dict):
        """Get search results from online sources.
        This method will use the agent's capabilities to search for information online.
        """
        Query = query['query']
        if query == "":
            return "Enter something "
        logger.info("Searching online")
        try:
           
            query = await self.queryAnalyser(query=Query)
            # Use the DDGS (DuckDuckGo Search) API to get search results
            # Initialize the DDGS object
            results = await agentService.getWebSearchData(query)
            # Process the results and return them in a structured format
            # Create a dictionary to store the results
            dataFromOnline = {}
            # Iterate through the results and extract relevant information
            # Store the results in the dictionary
            highestScore = 0
            for r in results:
                if await agentService.checkIsAllowedToScrap(url=r['href'],user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"):
                    contentFromWebPage = await getDataFromArticles(r['href'])
                    similarityScore = await agentService.checkSimilarity(context=contentFromWebPage,query=Query)
                    if similarityScore>0.5:
                        highestScore = similarityScore if similarityScore>highestScore else highestScore
                        dataFromOnline[similarityScore] = {
                            'url': r['href'],
                            'content in url': f"{r['body']}"+",".join(contentFromWebPage) 
                        }
                else:logger.info("notAllowed to scrap")
            # return the results
            return dataFromOnline[highestScore]
        except Exception as e:
            logger.info(f"Error during search : {e}")
            return {"status_code":400,"error":e}

async def getDataFromArticles(url:str):
    """Extract the data from link and structured it --> returning extracted data """
    pageHTML = requests.get(url=url)
    
    soup = BeautifulSoup(pageHTML.text,'html.parser')

    paras = soup.find_all('p') 
    contentFromWebPages = [str(text.text) for text in paras if text != ""]

    return contentFromWebPages