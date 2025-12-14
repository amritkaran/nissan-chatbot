# Nissan Knowledge Bot - OpenAI File Search Stack

A production-ready chatbot/voicebot for Nissan using OpenAI's Assistants API with File Search.

## Architecture

```
Firecrawl → OpenAI File Search → GPT-4o → Next.js + Deepgram + ElevenLabs
                                              ↓
                                        Ragas Evaluation
```

## Project Structure

```
nissan-chatbot-openai/
├── scraper/              # Firecrawl web scraping
│   ├── scraper.py        # Main scraping logic
│   └── config.py         # Scraping configuration
├── backend/              # OpenAI integration
│   ├── assistant.py      # OpenAI Assistants setup
│   ├── vector_store.py   # Vector store management
│   └── api.py            # FastAPI backend
├── frontend/             # Next.js web app
│   └── ...               # Next.js project files
├── evaluation/           # Ragas evaluation
│   ├── evaluate.py       # Evaluation pipeline
│   └── test_questions.json
├── data/
│   ├── raw/              # Raw scraped content
│   └── processed/        # Processed documents
└── .env.example          # Environment variables template
```

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Scrape Nissan Website

```bash
python scraper/scraper.py
```

### 4. Create OpenAI Assistant

```bash
python backend/assistant.py --setup
```

### 5. Run the Application

```bash
# Backend
python backend/api.py

# Frontend (separate terminal)
cd frontend && npm run dev
```

### 6. Evaluate with Ragas

```bash
python evaluation/evaluate.py
```

## API Keys Required

- `OPENAI_API_KEY` - OpenAI API key
- `FIRECRAWL_API_KEY` - Firecrawl API key
- `DEEPGRAM_API_KEY` - Deepgram API key
- `ELEVENLABS_API_KEY` - ElevenLabs API key
