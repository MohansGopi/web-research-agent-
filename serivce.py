import spacy
from duckduckgo_search import DDGS
import os
import time
import urllib.robotparser
from dotenv import load_dotenv
import random
from transformers import pipeline
from logger import logger

corrector = pipeline("text2text-generation", model="vennify/t5-base-grammar-correction")
nlp = spacy.load("en_core_web_sm")
modelForSimilarity = spacy.load("en_core_web_md")
load_dotenv()

MESSAGE =[]

INTENT_PATTERNS = {
"trend analysis": [
"how", "has", "have", "how has", "how have", "change", "changed",
"trend", "evolved", "growth", "evolution", "over", "time", "over time",
"progress", "shift"
],
"instructional": [
"how", "to", "how to", "steps", "step", "method", "process",
"way", "way to", "guide", "build", "create", "implement", "set", "up", "set up"
],
"definition": [
"what", "is", "what is", "define", "definition", "definition of",
"meaning", "meaning of", "explain", "describe"
],
"causal explanation": [
"why", "is", "does", "why is", "why does", "cause", "cause of",
"reason", "reason for", "what", "causes", "what causes"
],
"commercial": [
"buy", "purchase", "price", "cost", "best", "top", "cheap", "affordable",
"discount", "deal", "where", "to", "where to", "where to buy"
],
"opinion": [
"opinion", "review", "recommend", "suggest", "feedback", "thoughts","best ",
"thoughts on", "pros", "cons", "experience", "which is better","preffer","could"
],
"recent news": [
"latest", "breaking", "recent", "current", "today", "this week",
"news", "news about", "update", "update on","now","happening","happen","happened"
],
"informational": [
"information", "information about", "details", "details on",
"summary", "summary of", "facts", "background", "background on"
]
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
class services:
    async def getWebSearchData(self,query:str):
        """Search on web and return the links and snippets"""
        
        ddgs = DDGS(headers=headers)
        try:
            # Perform the search query
            response = ddgs.text(query)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    async def getIntentAndKeywordsOfQuery(self,Query:str):
        """Get intent and keywords of the query"""
        query_lower = Query.lower().strip()
        intent_=""
        for intent, patterns in INTENT_PATTERNS.items():
            if any(p in query_lower.split(" ") for p in patterns):
                intent_ = intent
                break
        intent_ = "informational" if intent_=="" else intent_
        return {"Intent":intent_,"Keywords":await self.getKeywordAndTopics(query_lower)}
    
    async def checkIsAllowedToScrap(self,url:str,user_agent:str):
        """check the site allows to scrap their data"""
        rp = urllib.robotparser.RobotFileParser()
        domain = url.split("/")[2]
        robots_url = f"https://{domain}/robots.txt"
        
        rp.set_url(robots_url)
        rp.read()
        
        return rp.can_fetch(user_agent, url)
    
    async def checkSimilarity(self,context:list,query:str):
        """Check the similarity between query and content in webpages"""
        print(len("".join(context)))
        contextvector =modelForSimilarity(("".join(context))[:1000000])
        queryvector = modelForSimilarity(query)

        similarities = queryvector.similarity(contextvector)
        return similarities
    
    async def spellCorrector(self,query:str):
        result = corrector(query, max_length=50)
        query = result[0]["generated_text"]
        return str(query)

    async def getKeywordAndTopics(self,Query:str):
        """Get keywords related to the query"""
        doc = nlp(Query)
        return [token.text for token in doc if token.is_alpha and not token.is_stop]
            