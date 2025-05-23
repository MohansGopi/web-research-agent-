import spacy
from duckduckgo_search import DDGS
import urllib.robotparser
import asyncio
from dotenv import load_dotenv
from transformers import pipeline
from logger import logger
import os
from groq import Groq
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Load environment variables
load_dotenv()

# Global model instances (loaded once)
nlp = spacy.load("en_core_web_sm")
modelForSimilarity = spacy.load("en_core_web_md")
corrector = pipeline("text2text-generation", model="vennify/t5-base-grammar-correction")
ddgs = DDGS(headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
})

message = []


class services:
    """Service class to perform web search, NLP processing, and similarity checking."""

    async def getWebSearchData(self, query: str):
        """Search the web using DuckDuckGo and return results."""
        try:
            return ddgs.text(query)
        except Exception as e:
            logger.error(f"Error during web search for '{query}': {e}")
            return []

    async def checkIsAllowedToScrap(self, url: str, user_agent: str):
        """Check if scraping is allowed based on robots.txt rules."""
        try:
            domain = url.split("/")[2]
            robots_url = f"https://{domain}/robots.txt"

            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            return rp.can_fetch(user_agent, url)
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            return False

    async def checkSimilarity(self, context: list, query: str):
        """Calculate the similarity between a webpage context and a user query."""
        try:
            if not context:
                return 0.0

            # Join and limit context size to 1 million characters
            context_text = "".join(context)[:1000000]

            context_vector = modelForSimilarity(context_text)
            query_vector = modelForSimilarity(query)

            similarity_score = query_vector.similarity(context_vector)
            return similarity_score
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    async def spellCorrector(self, query: str):
        """Correct spelling and grammar of a query."""
        try:
            result = corrector(query, max_length=50)
            return result[0]["generated_text"]
        except Exception as e:
            logger.error(f"Error correcting spelling for '{query}': {e}")
            return query

    async def getKeywordAndTopics(self, Query: str):
        """Extract keywords and topics from a query using NLP."""
        try:
            doc = nlp(Query)
            keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
            return keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    async def summarizer(self,query:str,context:str):
        """Summarize the context by the query"""
        message.append({"role": "user", "content": f"Query:{query}\nContext:{context}"})
        try:
            chat_completion = client.chat.completions.create(
            messages=message,
            model="llama3-70b-8192",)
            message.append({
            "role": "assistant",
            "content": chat_completion.choices[0].message.content})
            return chat_completion.choices[0].message.content
        except:
            return context
    
    async def convert_to_html(self,text:str):
        lines = text.strip().split('\n')
        html = ""
        for line in lines:
            # Section titles (bold and colon)
            if re.match(r"\*\*(.+?)\*\*:", line):
                section_title = re.findall(r"\*\*(.+?)\*\*:", line)[0]
                html += f"<h2>{section_title}</h2>\n"

            # Subsection headers like 1. Tokyo - ...
            elif re.match(r"\d+\.\s.+? - ", line):
                title, desc = line.split(" - ", 1)
                html += f"<h3>{title.strip()}</h3>\n<p>{desc.strip()}</p>\n"

            # Bulleted items
            elif line.strip().startswith("* "):
                if not html.endswith("<ul>\n"):
                    html += "<ul>\n"
                html += f"<li>{line.strip()[2:]}</li>\n"

            # Empty line - used to close any open <ul>
            elif line.strip() == "":
                if html.endswith("<ul>\n") or "<li>" in html[-10:]:
                    html += "</ul>\n"

            # Fallback: plain paragraph
            else:
                html += f"<p>{line.strip()}</p>\n"

        # Close list if open
        if html.endswith("<ul>\n") or "<li>" in html[-10:]:
            html += "</ul>\n"

        return html