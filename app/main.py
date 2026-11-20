import os
import json
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.config import FREE_MODELS, DEFAULT_MODEL, APP_TITLE, PORT
from app.rag import retriever
from app.openrouter import call_openrouter

app = FastAPI(title=APP_TITLE, version="1.0.0")

# Setup templates and static files
BASE_DIR = os.path.dirname(__file__)
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

class MessageItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageItem]
    model: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": APP_TITLE,
            "models": FREE_MODELS,
            "default_model": DEFAULT_MODEL,
            "total_properties": len(retriever.items)
        }
    )

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "app": APP_TITLE,
        "total_knowledge_records": len(retriever.items),
        "free_models_available": len(FREE_MODELS)
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty.")
    
    # Get last user query
    user_query = req.messages[-1].content
    
    # RAG search across DarGlobal and Wasalt unified knowledge base
    search_result = retriever.search(user_query, top_k=4)
    context = search_result.get("context", "")
    matched_properties = search_result.get("properties", [])
    
    # Call OpenRouter with strictly free models and cascading fallback
    dict_messages = [{"role": m.role, "content": m.content} for m in req.messages]
    llm_res = call_openrouter(
        messages=dict_messages,
        context=context,
        preferred_model=req.model
    )
    
    return JSONResponse({
        "reply": llm_res["reply"],
        "model_used": llm_res["model_used"],
        "status": llm_res["status"],
        "properties": matched_properties
    })

@app.get("/api/properties")
async def get_properties(
    source: Optional[str] = None, 
    region: Optional[str] = None, 
    query: Optional[str] = None
):
    items = retriever.items
    if source:
        items = [i for i in items if i.get("source", "").lower() == source.lower()]
    if region:
        items = [i for i in items if region.lower() in (i.get("location", "") + i.get("region", "")).lower()]
    if query:
        q = query.lower()
        items = [i for i in items if q in (i.get("title", "") + i.get("description", "")).lower()]
        
    return JSONResponse({
        "total": len(items),
        "data": items
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=False)
