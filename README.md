13. README.md
# Agentic AI Fund Search Application

A production-grade, scalable FastAPI application that integrates an agentic AI system using LangGraph, enabling intelligent search, summarization, and reasoning over mutual fund data from MFAPI.in.

## Features

- *Agentic AI Framework*: Built with LangGraph for intelligent reasoning
- *Real-time Fund Data*: Connects to MFAPI.in for latest mutual fund information
- *Natural Language Queries*: Ask questions about funds in plain English
- *Comparison Engine*: Compare multiple funds with detailed analysis
- *Streaming Responses*: Get real-time streaming responses from the AI
- *Production Ready*: Built with FastAPI for high performance and scaling

## Tech Stack

- FastAPI
- LangGraph
- OpenAI
- MFAPI.in
- Pydantic
- Pytest
- Docker

## API Endpoints

- GET /funds/search?q=bluechip - Search for funds by name/keyword
- GET /funds/{scheme_code} - Get details for a specific fund
- POST /funds/compare - Compare multiple funds
- POST /ai/query - Ask questions in natural language
- POST /ai/query/stream - Stream AI responses for questions

## Setup & Installation

### Using Docker

bash
# Clone the repository
git clone https://github.com/yourusername/agentic-mfapi-ai.git
cd agentic-mfapi-ai

# Create .env file from example
cp .env.example .env
# Edit .env and add your OpenAI API key

# Start with Docker Compose
docker-compose up


### Manual Setup

bash
# Clone the repository
git clone https://github.com/yourusername/agentic-mfapi-ai.git
cd agentic-mfapi-ai

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run the application
uvicorn app.main:app --reload


## 🧪 Running Tests

bash
pytest


## Example Usage

### Ask a Question

bash
curl -X POST "http://localhost:8000/api/ai/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Compare SBI Bluechip with ICICI Bluechip fund"}'


### Search for Funds

bash
curl "http://localhost:8000/api/funds/search?q=hdfc%20top%20100"


### Get Fund Details

bash
curl "http://localhost:8000/api/funds/119010"


### Compare Funds

bash
curl -X POST "http://localhost:8000/api/funds/compare" \
  -H "Content-Type: application/json" \
  -d '{"scheme_codes": [119010, 120465], "period": "1y"}'


## Project Structure


agentic-mfapi-ai/
├── app/
│   ├── agents/            # LangGraph agents
│   ├── api/               # FastAPI routes
│   ├── services/          # mfapi wrappers
│   ├── schemas/           # Pydantic models
│   ├── core/              # Configs, LLM client
│   └── main.py            # FastAPI entrypoint
├── tests/                 # Test cases
├── README.md              # This file
├── requirements.txt       # Dependencies
└── .env                   # Environment variables
