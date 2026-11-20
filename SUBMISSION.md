# DarGlobal Technical Assignment Submission

**Candidate:** Junior AI Engineer – Applied AI Applicant  
**Position:** Junior AI Engineer – Applied AI  
**Recipient:** careers@darglobal.co.uk  
**Submission Date:** Friday, 20 Nov 2026  

---

## 1. Executive Summary & Live Application URL

- **GitHub Repository:** [https://github.com/bingoabdulla7/DarGlobal-Wasalt-Real-Estate-Advisor](https://github.com/bingoabdulla7/DarGlobal-Wasalt-Real-Estate-Advisor)
- **Live Working URL:** [https://606a753812e506.app.lhr.life](https://606a753812e506.app.lhr.life)
- **Local Application URL:** `http://localhost:8000`
- **Container Health Check:** [https://606a753812e506.app.lhr.life/healthz](https://606a753812e506.app.lhr.life/healthz)
- **Portfolio API Endpoint:** [https://606a753812e506.app.lhr.life/api/properties](https://606a753812e506.app.lhr.life/api/properties)

---

## 2. Technical Implementation Highlights

### 1. Data Ingestion & Scraping
- **DarGlobal (`scripts/scrape_darglobal.py`)**: Extracted all 38 premier international developments directly from DarGlobal's official Strapi CMS API (`https://strapi.darglobal.co.uk/api/projects?populate=Tabs`), including luxury branded collaborations with **The Trump Organization, Automobili Lamborghini, Pagani Automobili, Aston Martin, Elie Saab, Missoni, Mouawad, and Marriott**.
- **Wasalt (`scripts/scrape_wasalt.py`)**: Extracted 40+ verified properties across Saudi Arabia (Riyadh, Jeddah, etc.) with real pricing (SAR), bedroom/bathroom configurations, square meterage, district/neighborhood information, and **Saudi REGA licensing numbers**.
- **Unified Knowledge Store (`data/knowledge_base.json`)**: 81 standardized records with corporate profiles and investment comparison guides.

### 2. Hybrid RAG & OpenRouter Intelligence
- **Retrieval Engine**: BM25 & token-level semantic retrieval with attribute boosters for location, developer, brand partner, and property type.
- **Strictly Free Inference**: Enforces 100% free models on OpenRouter (`openrouter/free`, `google/gemma-4-31b-it:free`, `nvidia/nemotron-3.5-lightning:free`, `particle-ai/particle-1:free`, etc.) with zero inference cost.
- **Dual API Key Rotation & Cascading Failover**: Configured with primary and secondary keys to withstand rate limits and automatically fail over across 12+ free models.
- **Bilingual Support**: Fluent, grounded real estate advisory in both English and Arabic.

### 3. Frontend Experience
- Modern FastAPI + Tailwind CSS Single-Page Application matching DarGlobal's dark/gold luxury branding.
- Inline **Interactive Property Cards** with high-resolution imagery, pricing, bedroom counts, completion dates, and direct links to official listings.
- "Portfolio Directory" modal allowing reviewers to browse and search all 81 scraped properties.

### 4. Containerization & Production Readiness
- **Dockerfile**: Optimized multi-stage `python:3.11-slim` container with non-root security user, built-in healthcheck, and sub-150MB footprint.
- **Docker Compose**: Single-command startup (`docker compose up --build`).
- **Render Ready**: Includes `render.yaml` for zero-configuration cloud deployment on Render.

---

## 3. Email Submission Template

**To:** `careers@darglobal.co.uk`  
**Subject:** Technical Assignment Submission – Junior AI Engineer (Applied AI) – [Your Full Name]  

```
Dear DarGlobal Hiring Team,

Thank you for the opportunity to complete the technical assignment for the Junior AI Engineer – Applied AI role.

I have completed the end-to-end task and deployed the live AI Chatbot solution. You can access and test the live application directly at the link below:

🔗 Live Working Application URL:
https://606a753812e506.app.lhr.life

📦 GitHub Repository:
https://github.com/bingoabdulla7/DarGlobal-Wasalt-Real-Estate-Advisor

Project Highlights:
1. Data Scraping & Normalization:
   - Scraped all 38 luxury international developments from DarGlobal (Dubai, Spain, Oman, London, Qatar, and KSA) including branded collaborations with Trump, Lamborghini, Pagani, Aston Martin, Elie Saab, and Missoni.
   - Scraped 40+ verified domestic residential and commercial properties in Saudi Arabia from Wasalt with REGA regulatory licensing, pricing in SAR, and neighborhood details.
   - Synthesized into a unified 81-record searchable real estate knowledge base.

2. AI Intelligence & Strict Free Tier OpenRouter:
   - Built a hybrid RAG pipeline retrieving relevant properties with location and brand-matching boosters.
   - Powered strictly by free models on OpenRouter (primary auto-router and top free instruction models such as Gemma and Nemotron).
   - Implemented dual-key rotation and multi-model fallback to ensure continuous availability.
   - Fluent bilingual advisory in both English and Arabic.

3. Frontend & User Experience:
   - Built a custom luxury single-page application using FastAPI and Tailwind CSS matching DarGlobal's black and gold aesthetic.
   - Features dynamic inline Property Cards with images, pricing, completion dates, and direct listing links.
   - Includes an interactive Portfolio Directory modal exploring all 81 scraped properties.

4. Containerization & Deployment:
   - Fully containerized with a lightweight Dockerfile and docker-compose.yml.
   - Render deployment blueprint (render.yaml) and comprehensive README documentation included.

I look forward to discussing the implementation and how I can contribute to DarGlobal's Applied AI initiatives.

Best regards,
[Your Full Name]
[Your Phone Number]
[Your LinkedIn / GitHub Profile]
```
