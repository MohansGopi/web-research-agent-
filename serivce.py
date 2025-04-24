import spacy
nlp = spacy.load("en_core_web_sm")

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
"opinion", "review", "recommend", "suggest", "feedback", "thoughts",
"thoughts on", "pros", "cons", "experience", "which is better","preffer"
],
"recent news": [
"latest", "breaking", "recent", "current", "today", "this week",
"news", "news about", "update", "update on"
],
"informational": [
"information", "information about", "details", "details on",
"summary", "summary of", "facts", "background", "background on"
]
}
class services:
    async def getIntentAndKeywordsOfQuery(self,Query:str):
        """Get intent and keywords of the query"""
        query_lower = Query.lower().strip()
        intent_=""
        for intent, patterns in INTENT_PATTERNS.items():
            if any(p in query_lower.split(" ") for p in patterns):
                intent_ = intent
                break
        intent_ = "informational" if intent_=="" else intent_
        return {"Intent":intent_,"Keywords":await getKeywordAndTopics(query_lower)}
    


async def getKeywordAndTopics(Query:str):
    """Get keywords related to the query"""
    doc = nlp(Query)
    return [token.text for token in doc if token.is_alpha and not token.is_stop]