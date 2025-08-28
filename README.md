# Web Research Agent  

## 📌 Overview  
The **Web Research Agent** is a Python-based tool for automated web research. It allows users to query the web, collect relevant information, and summarize results into concise outputs. Designed with modular components, it can be extended for investment research, market analysis, or general-purpose information retrieval.  

## ⚙️ Features  
- 🌐 Web query handling  
- 📑 Automatic summarization of results  
- 🚀 API endpoints for integration (FastAPI/Flask)  
- 🛠 Modular service-controller architecture  

## 📂 Project Structure  
```
.
├── .env                 # Environment variables  
├── controller.py        # Core business logic  
├── router.py            # API routes  
├── serivce.py           # Service layer (possible typo, should be service.py)  
├── summarizer.py        # Summarization logic  
├── requirements.txt     # Dependencies  
├── README.md            # Documentation  
└── .agentENV/           # Virtual environment (should be ignored in .gitignore)  
```  

## 🚀 Installation  

1. Clone the repository  
   ```bash
   git clone https://github.com/your-repo/web-research-agent.git
   cd web-research-agent
   ```

2. Create and activate a virtual environment  
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows
   ```

3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`  

## ▶️ Usage  

Start the API server:
```bash
uvicorn router:app --reload
```

Send a request:
```bash
curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d '{"query":"latest AI research"}'
```

Response will include summarized research results.  

## 📌 Notes  
- `.agentENV/` (the included virtual environment) should **not** be part of version control. Add it to `.gitignore`.  
- Rename `serivce.py` → `service.py` for clarity.  

## 🏗️ Future Improvements  
- Add a frontend UI for queries  
- Enhance summarizer with LLM integration  
- Support multiple data sources (news, research papers, social media)  
