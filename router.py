from fastapi import FastAPI,Request
from controller import agentController
from fastapi.middleware.cors import CORSMiddleware
from serivce import services

# This is the main entry point for the FastAPI application.
app = FastAPI(
    title="web-research-agent -- deployment phase",
    description="A web research agent that can scrape and analyze web pages.",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 Allow all origins (You can make it specific later)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
phrases = [
    "hello",
    "hi",
    "hii",
    "hey",
    "hey there",
    "how are you",
    "how r u",
    "how are u",
    "who are you",
    "who r u",
    "what's up",
    "whats up",
    "sup",
    "yo",
    "good morning",
    "good night",
    "good evening",
    "good afternoon",
    "long time no see",
    "how's it going",
    "what you doing",
    "what are you doing",
    "what r u doing",
    "wyd",
    "where are you",
    "where r u",
    "what's going on",
    "wassup",
    "nice to meet you",
    "nice meeting you",
    "how have you been",
    "hi there",
    "hello there"
]


# Initialize the agentController
control = agentController()
service = services()
# Define a api endpoint

@app.post("/getData")
async def get_data(query: Request):
    """Endpoint to get data from the agentController."""
    data = await query.json()
    try:
        if data in phrases:
            raw_text = await service.summarizer(data)
            contextFromOnline = await service.convert_to_html(raw_text)
        else:
            contextFromOnline = await control.getSearchFromOnline(data)

        return contextFromOnline
    except:
        return {'content in url':"Server busy - Try again after sometime"}
    
