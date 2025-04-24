# -*- coding: utf-8 -*-
from duckduckgo_search import DDGS
from logger import logger
from bs4 import BeautifulSoup
import requests
from serivce import services
from datetime import datetime
from dotenv import load_dotenv
import os,random
from spellchecker import SpellChecker

load_dotenv()
agentService = services()
spell = SpellChecker()

class agentController:
    """Controller for the agent class.
    This class is responsible for handling the agent's actions and interactions with the web.
    """
    async def queryAnalyser(self,query:str):
        """Analyse the query for breakdown complex question in searchable compontents"""
        logger.info("Analyzing query")
        # Get the intent and keyword of the query by getIntentOfQuery function
        querySpellChecker = spell.unknown(query.split(' '))
        
        for word in querySpellChecker:
            query= query.replace(word,spell.correction(word))
        
        queryIntentAndKeywords = await agentService.getIntentAndKeywordsOfQuery(query)

        if queryIntentAndKeywords['Intent'] == "recent news" : query+=f"{os.getenv("NEWS_BASE_URL_STR")},inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "trend analysis" : query+=f" today's date : {datetime.now().date()},inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "instructional" : query+=f"{os.getenv("INSTRUCTION_BASE_URL_STR")},inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "definition" : query+=f"{os.getenv("DEFINITION_BASE_URL_STR")},inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "causal explanation" : query+=f"{os.getenv("CE_BASE_URL_STR")},inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "opinion" : query+=f"{os.getenv("OPIN_BASE_URL_STR")},inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "commercial" : query+=f"{os.genenv("COMMERCIAL_BASE_URL_STR")},inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        elif queryIntentAndKeywords['Intent'] == "informational" : query+=f" inurl:{random.choice(queryIntentAndKeywords['Keywords'])}"
        print(query)
        return query


    async def getSearchFromOnline(self,query:dict):
        """Get search results from online sources.
        This method will use the agent's capabilities to search for information online.
        """
        query = query['query']
        print(query)
        if query == "":
            return "Enter something "
        logger.info("Searching online")
        try:
            query = await self.queryAnalyser(query=query)
            # Use the DDGS (DuckDuckGo Search) API to get search results
            # Initialize the DDGS object
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=5)
            # Process the results and return them in a structured format
            # Create a dictionary to store the results
            dataFromOnline = {}
            # Iterate through the results and extract relevant information
            # Store the results in the dictionary
            for r in results:
                dataFromOnline[r['title']] = {
                    'title': r['title'],
                    'url': r['href'],
                    'content in url': await getDataFromArticles(r['href']),
                    'snippet': r['body']
                }
            # return the results
            return dataFromOnline
        except Exception as e:
            logger.info(f"Error during search : {e}")
            return ("something went wrong")

async def getDataFromArticles(url:str):
    """Extract the data from link and structured it --> returning extracted data """
    pageHTML = requests.get(url=url)
    
    soup = BeautifulSoup(pageHTML.text,'html.parser')
    
    contentFromWebPages = [text.strip() for text in str(soup.text).split("\n") if text != ""]

    return contentFromWebPages