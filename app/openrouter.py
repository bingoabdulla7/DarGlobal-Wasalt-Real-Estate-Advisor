import urllib.request
import urllib.error
import json
import logging
from typing import Generator, Dict, Any, List, Optional
from app.config import API_KEYS, FREE_MODELS, DEFAULT_MODEL

logger = logging.getLogger("openrouter")
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """You are the official AI Real Estate Advisor for DarGlobal and Wasalt.
Your goal is to provide elite advisory services to prospective buyers, luxury investors, and property seekers exploring:
1. DarGlobal's international luxury developments (branded residences across Dubai, London, Spain, Oman, Qatar, and Saudi Arabia in partnership with brands like Trump, Lamborghini, Pagani, Missoni, Elie Saab, Aston Martin, and Mouawad).
2. Wasalt's verified domestic real estate marketplace across Saudi Arabia (residential villas, apartments, duplexes, commercial land in Riyadh, Jeddah, and across the Kingdom, regulated under REGA).

Advisory Guidelines:
- Ground your answers in the PROVIDED REAL ESTATE CONTEXT. Always reference specific project titles, locations, luxury brand partners, amenities, and pricing details when available.
- If the user asks about luxury international investments or branded residences, highlight relevant DarGlobal developments.
- If the user asks about domestic Saudi properties, family homes, or local listings in Riyadh/Jeddah, highlight Wasalt verified properties.
- When comparing, explain that DarGlobal caters to ultra-luxury global lifestyle and trophy assets, while Wasalt is Saudi Arabia's premier domestic marketplace for living and local investments (both part of the Dar Al Arkan heritage).
- Provide official listing links when available so users can explore and book viewings.
- Tone: Sophisticated, courteous, authoritative, and helpful.
- Support both English and Arabic naturally based on the user's language.
- Format cleanly with bullet points, bold highlights, and clear sections.
"""

def call_openrouter(
    messages: List[Dict[str, str]], 
    context: str = "", 
    preferred_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calls OpenRouter with strict free model enforcement, multi-key rotation,
    and automatic cascading fallback across free models.
    """
    if not API_KEYS:
        raise ValueError("No OpenRouter API keys configured in environment or .env file.")

    # Prepare messages with system prompt and retrieved context
    enriched_system = SYSTEM_PROMPT
    if context:
        enriched_system += f"\n\n--- CURRENT RETRIEVED REAL ESTATE CONTEXT ---\n{context}\n-------------------------------------------"

    full_messages = [{"role": "system", "content": enriched_system}]
    # Add conversation history
    for m in messages:
        if m.get("role") in ["user", "assistant"]:
            full_messages.append({"role": m["role"], "content": m["content"]})

    # Models list to attempt (strictly free only)
    candidate_models = list(FREE_MODELS)
    if preferred_model and preferred_model in FREE_MODELS:
        candidate_models.remove(preferred_model)
        candidate_models.insert(0, preferred_model)

    last_error = None
    
    # Try models and keys with graceful fallback
    for model in candidate_models:
        for key_idx, key in enumerate(API_KEYS):
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://darglobal.co.uk",
                "X-Title": "DarGlobal & Wasalt Real Estate AI"
            }
            
            payload = {
                "model": model,
                "messages": full_messages,
                "max_tokens": 1200,
                "temperature": 0.4
            }
            
            try:
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choices = data.get("choices", [])
                    if choices:
                        msg = choices[0].get("message", {})
                        content = msg.get("content") or choices[0].get("text") or ""
                        
                        # Some reasoning models return reasoning field or empty content if stopped early
                        if not content and "reasoning" in msg and msg["reasoning"]:
                            content = msg["reasoning"]
                            
                        if content.strip():
                            model_used = data.get("model", model)
                            return {
                                "reply": content.strip(),
                                "model_used": model_used,
                                "status": "success"
                            }
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8", errors="ignore")
                logger.warning(f"Model {model} with Key #{key_idx+1} returned HTTP {e.code}: {err_text[:120]}")
                last_error = f"HTTP {e.code}: {err_text[:100]}"
                continue # Try next key or next model
            except Exception as e:
                logger.warning(f"Model {model} with Key #{key_idx+1} error: {e}")
                last_error = str(e)
                continue

    # If all models failed or rate limited, return a graceful fallback advisory response based on context
    logger.error(f"All free models exhausted. Last error: {last_error}")
    return {
        "reply": (
            "I am currently receiving an extraordinarily high volume of requests on the free inference gateway. "
            "However, based on our verified portfolio records:\n\n"
            + (context if context else "Please browse our highlighted projects below or try again in a few moments.")
        ),
        "model_used": "offline-rag-fallback",
        "status": "fallback"
    }
