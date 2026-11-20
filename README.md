# DarGlobal & Wasalt Real Estate AI Advisor

[![Docker Containerized](https://img.shields.io/badge/Docker-Containerized-blue.svg)](Dockerfile)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![OpenRouter](https://img.shields.io/badge/Inference-OpenRouter%20Free%20Tier-purple.svg)](https://openrouter.ai)
[![Status](https://img.shields.io/badge/Deployment-Render%20Ready-success.svg)](render.yaml)

A production-grade, containerized AI Chatbot and Real Estate Advisory Platform developed for the **Junior AI Engineer – Applied AI** technical assignment at **DarGlobal**.

The system is grounded on publicly scraped real estate data from **DarGlobal** (luxury international developer listed on LSE) and **Wasalt** (leading Saudi Arabian real estate marketplace), powered strictly by **free models on OpenRouter** with automatic multi-key rotation and multi-model fallback, featuring an ultra-luxury responsive web interface.

---

## Architecture Overview

```
                      ┌─────────────────────────────────────────┐
                      │             Web Browser (UI)            │
                      │  Luxury Dark/Gold SPA with Interactive   │
                      │       Property Cards & Streaming        │
                      └────────────────────┬────────────────────┘
                                           │ HTTP / JSON
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │          FastAPI Web Application        │
                      │       (Endpoints: /, /api/chat,         │
                      │      /api/properties, /healthz)         │
                      └───────┬─────────────────────────┬───────┘
                              │                         │
                 Hybrid Search│                         │ LLM Prompt & Fallback
                              ▼                         ▼
┌──────────────────────────────────────┐       ┌─────────────────────────────────────┐
│       Hybrid RAG Engine (rag.py)     │       │   OpenRouter Client (openrouter.py) │
│ - Tokenized & Attribute BM25 Search  │       │ - Multi-Key Rotation (Key 1 -> 2)   │
│ - Lexical & Brand Filters (Trump,    │       │ - Strict Free Model Cascading:      │
│   Lamborghini, Missoni, Wasalt KSA)  │       │   * openrouter/free                 │
│ - Unified Knowledge Base (81 Items)  │       │   * google/gemma-4-31b-it:free      │
└──────────────────────────────────────┘       │   * nvidia/nemotron-3.5-lightning   │
                                               │   * particle-ai/particle-1:free     │
                                               │   * 12+ Active Free Models          │
                                               └─────────────────────────────────────┘
```

---

## 1. Scraped Datasets

The platform ingests and standardizes data across both official digital properties:

1. **DarGlobal (`scripts/scrape_darglobal.py`)**:
   - Extracted directly from DarGlobal's official headless Strapi CMS API (`https://strapi.darglobal.co.uk/api/projects?populate=Tabs`).
   - Contains **38 premier international developments** across the UAE, Spain, UK, Oman, Qatar, and Saudi Arabia.
   - Includes branded collaborations with **The Trump Organization, Automobili Lamborghini, Pagani Automobili, Aston Martin, Elie Saab, Missoni, Mouawad, and Marriott**.

2. **Wasalt (`scripts/scrape_wasalt.py`)**:
   - Extracted from Wasalt's official Next.js Server-Side Rendered (SSR) property endpoints and product sitemap (`https://cdn.wasalt.sa/sitemap/product_sitemap_en_sa.xml.gz`).
   - Contains **40+ verified domestic Saudi properties** across Riyadh, Jeddah, and surrounding regions.
   - Includes real pricing (SAR), bedroom/bathroom configurations, square meterage, district/neighborhood information, and **Saudi REGA licensing numbers**.

3. **Unified Knowledge Store (`scripts/build_knowledge_base.py`)**:
   - Synthesizes all 81 project/property records with corporate background guides, investment comparison articles, and bilingual indexation.

---

## 2. Key Features

- **Strictly Free OpenRouter Models**: Uses 100% free models (`openrouter/free`, `google/gemma-4-31b-it:free`, `nvidia/nemotron-3.5-lightning:free`, `particle-ai/particle-1:free`, etc.) with zero inference cost.
- **Dual API Key Rotation & Cascading Failover**: Configured with primary and secondary OpenRouter keys. If Key 1 hits rate-limit (HTTP 429) or a model is temporarily saturated, the system automatically rotates keys and falls back to the next free model.
- **Interactive Property Cards**: Whenever projects are recommended, rich interactive cards with thumbnail photos, pricing, bedroom counts, completion dates, and direct links to official listings are rendered inline in the chat.
- **Portfolio Directory Modal**: Reviewers can click "Portfolio Directory" to search, filter, and view all 81 properties across DarGlobal and Wasalt.
- **Bilingual Intelligence**: Capable of conversing naturally in both English and Arabic.
- **Ultra-Lightweight & Fast**: Pure Python + FastAPI with no heavy GPU/PyTorch overhead; Docker container is under 150 MB and boots in under 2 seconds.

---

## 3. Local Setup & Docker Execution

### Option A: Running with Docker (Recommended)

1. **Clone the repository and ensure `.env` is configured**:
   ```bash
   # .env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_API_KEY_FALLBACK=your_openrouter_fallback_key_here
   ```

2. **Build and run using Docker Compose**:
   ```bash
   docker compose up --build
   ```

3. **Or build with standard Docker CLI**:
   ```bash
   docker build -t darglobal-ai .
   docker run -p 8000:8000 --env-file .env darglobal-ai
   ```

4. **Access the application**:
   Open [http://localhost:8000](http://localhost:8000) in your browser.

---

### Option B: Running Locally with Python

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run tests**:
   ```bash
   python tests/test_app.py
   ```

3. **Start the application**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## 4. Deployment on Render

This repository includes a native `render.yaml` blueprint for 1-click cloud deployment on Render's free tier.

### Step-by-Step Deployment:
1. Push this repository to GitHub (e.g. `https://github.com/your-username/darglobal-wasalt-ai`).
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → **Web Service** → Connect your GitHub repository.
4. Render automatically detects the `Dockerfile` and `render.yaml`:
   - **Environment:** Docker
   - **Plan:** Free
   - **Health Check Path:** `/healthz`
5. Under **Environment Variables**, add:
   - `OPENROUTER_API_KEY`: `your_primary_key_here`
   - `OPENROUTER_API_KEY_FALLBACK`: `your_fallback_key_here`
6. Click **Deploy Web Service**.
7. Once build completes, Render will provide your live URL (e.g., `https://darglobal-wasalt-ai.onrender.com`).

---

## 5. Sample Prompts for Evaluators

1. **Dubai Branded Projects**:  
   *"What luxury branded projects does DarGlobal offer in Dubai?"*
2. **Saudi Domestic Properties**:  
   *"Find 4-bedroom or 5-bedroom villas in Riyadh from Wasalt."*
3. **Automotive Collaborations**:  
   *"Tell me about the Tierra Viva Lamborghini villas in Spain."*
4. **Resort & Cliffside Living**:  
   *"What is AIDA in Oman and what residences are available there?"*
5. **Ecosystem & Strategy**:  
   *"Explain how DarGlobal and Wasalt work together under the Dar Al Arkan umbrella."*
6. **Arabic Language Capability**:  
   *"ما هي المشاريع المتاحة في الرياض وما هي تفاصيل ترامب تاور دبي؟"*

---

## 6. Project Structure

```
DarGlobal/
├── .env                         # API keys (Primary & Fallback)
├── .gitignore                   # Excludes secrets & caches
├── Dockerfile                   # Multi-stage production container
├── docker-compose.yml           # Local single-command orchestration
├── render.yaml                  # Render deployment blueprint
├── requirements.txt             # Lightweight dependencies
├── README.md                    # System documentation
├── app/
│   ├── __init__.py
│   ├── config.py                # Environment configuration & model list
│   ├── main.py                  # FastAPI application & REST endpoints
│   ├── openrouter.py            # OpenRouter client with dual-key rotation
│   ├── rag.py                   # Hybrid knowledge retriever & card builder
│   ├── static/
│   │   ├── css/style.css        # Luxury dark/gold CSS theme
│   │   └── js/app.js            # Client-side chat, cards, and modal logic
│   └── templates/
│       └── index.html           # Single-page responsive web app
├── data/
│   ├── darglobal_projects.json  # 38 scraped DarGlobal luxury projects
│   ├── wasalt_properties.json   # 40+ scraped Wasalt verified properties
│   └── knowledge_base.json      # Unified 81-record searchable database
├── scripts/
│   ├── scrape_darglobal.py      # Automated DarGlobal Strapi scraper
│   ├── scrape_wasalt.py         # Automated Wasalt Next.js SSR scraper
│   └── build_knowledge_base.py  # Knowledge synthesizer & indexer
└── tests/
    └── test_app.py              # End-to-end integration test suite
```
