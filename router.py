from fastapi import FastAPI,Request
from controller import agentController

# This is the main entry point for the FastAPI application.
app = FastAPI(
    title="web-research-agent -- final phase",
    description="A web research agent that can scrape and analyze web pages.",
    version="0.2.0"
)

# Initialize the agentController
control = agentController()

# Define a root endpoint
@app.get("/")
async def root():
    return {"message": "Hello World", "context": "contextFromOnline"}


@app.post("/getData")
async def get_data(query: Request):
    """Endpoint to get data from the agentController."""
    data = await query.json()
    contextFromOnline = await control.getSearchFromOnline(data)
    return contextFromOnline
