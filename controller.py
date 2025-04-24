# -*- coding: utf-8 -*-
from duckduckgo_search import DDGS
from logger import logger

class agentController:
    """Controller for the agent class.
    This class is responsible for handling the agent's actions and interactions with the web.
    """
    def getSearchFromOnline(self,query:str):
        """Get search results from online sources.
        This method will use the agent's capabilities to search for information online.
        """
        logger.info("Searching online for: %s", query)
        # Use the DDGS (DuckDuckGo Search) API to get search results
        # Initialize the DDGS object
        with DDGS() as ddgs:
            results = ddgs.text(query['query'], max_results=5)

        # Process the results and return them in a structured format
        # Create a dictionary to store the results
        dataFromOnline = {}
        # Iterate through the results and extract relevant information
        # Store the results in the dictionary
        for r in results:
            dataFromOnline[r['title']] = {
                'title': r['title'],
                'url': r['href'],
                'snippet': r['body']
            }
        # Log the results
        return dataFromOnline