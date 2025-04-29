from fastapi import FastAPI,Request
from controller import agentController
from fastapi.middleware.cors import CORSMiddleware
from summarizer import Text_summarization

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

# Initialize the agentController
control = agentController()

# Define a api endpoint

@app.post("/getData")
async def get_data(query: Request):
    """Endpoint to get data from the agentController."""
    data = await query.json()
    try:
        contextFromOnline = await control.getSearchFromOnline(data)

        return contextFromOnline
    except:
        return {'content in url':"Server busy - Try again after sometime"}
