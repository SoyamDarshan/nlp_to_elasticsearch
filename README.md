# NL Prompt to Elasticsearch System

This project demonstrates a full-stack system that takes a natural language prompt from a React frontend, routes it through a Spring Boot Java API, processes it in a Python microservice (using an LLM to generate an Elasticsearch query), and renders results dynamically in a smart canvas.

## Project Structure
- `frontend/` — React app for user interaction
- `java-api/` — Spring Boot API for routing
- `python-service/` — Python Flask microservice for LLM and Elasticsearch

## Prerequisites
## Environment Variables

Before running the Python service, create a `.env` file in the `python-service/` directory with the following content:

```env
# .env for python-service
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=models/gemini-2.5-flash
ES_HOST=elasticsearch
ES_PORT=9200
```

Replace `your-gemini-api-key-here` with your actual Gemini API key.
- Docker & Docker Compose
- Node.js (for local frontend dev)
- Java 17+ (for local Java API dev)
- Python 3.8+ (for local Python dev)


## Quick Start (with Docker Compose)


### Build and start all services
```bash
docker-compose up --build
```

### Access the frontend
Open your browser to: [http://localhost:3000](http://localhost:3000)

### Stop all services
Press `Ctrl+C` in the terminal where Docker Compose is running, then:
```bash
docker-compose down
```

### Clean up all containers, networks, and volumes
```bash
docker-compose down -v
```


## Python Service Details
- Modularized: logic is split into `app.py`, `api.py`, `llm.py`, `models.py`.
- LLM: Uses Gemini (Google Generative AI) for query generation if `GEMINI_API_KEY` is set.
- Elasticsearch: Run `python populate_elasticsearch.py` to load data into Elasticsearch for testing or after changes to the data files.

## Elasticsearch
- Make sure Elasticsearch is running (Docker Compose will handle this). Populate it with `python-service/populate_elasticsearch.py` if you update the data files or want to reset the index.

## Example Queries

You can use natural language queries like:

- `show me log4jscanner:1.0.0`
- `show me CVE-2020-1472`

These will return details for the Log4jScanner component (version 1.0.0) and the CVE-2020-1472 vulnerability, respectively, if present in the Elasticsearch index.

## Endpoints
- **Frontend**
  - `/` — React UI
- **Java API** (`/api`)
  - `POST /api/nlp-query` — Accepts `{ "prompt": "..." }`, returns intent and results from Python service.
  - `POST /api/repopulate-es` — Triggers Elasticsearch repopulation via Python service, returns status.
- **Python Service**
  - `POST /process` — Accepts `{ "prompt": "..." }`, returns `{ intent, results }` (LLM → ES query).
  - `POST /repopulate-es` — Repopulates Elasticsearch index from data files, returns status.
