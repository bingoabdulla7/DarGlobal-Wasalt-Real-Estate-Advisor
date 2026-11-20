import urllib.request
import urllib.error
import json
import logging
import re
from typing import Generator, Dict, Any, List, Optional
from app.config import API_KEYS, FREE_MODELS, DEFAULT_MODEL

logger = logging.getLogger("openrouter")
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """You are the official AI Real Estate Advisor for DarGlobal and Wasalt.
Your goal is to provide elite advisory services to prospective buyers, luxury investors, and property seekers exploring:
1. DarGlobal's international luxury developments (branded residences across Dubai, London, Spain, Oman, Qatar, and Saudi Arabia in partnership with brands like Trump, Lamborghini, Pagani, Missoni, Elie Saab, Aston Martin, and Mouawad).
2. Wasalt's verified domestic real estate marketplace across Saudi Arabia (residential villas, apartments, duplexes, commercial land in Riyadh, Jeddah, and across the Kingdom, regulated under REGA).

CRITICAL RESPONSE RULES:
- Output ONLY your final, polished advisory response to the user.
- NEVER output any internal thinking, reasoning steps, translation notes, planning remarks, or commentary to yourself (e.g. NEVER write "The user is asking in...", "Key points from guidelines:", "I need to act as...", "Looking at the provided context:").
- If the user asks in Arabic, reply DIRECTLY and ENTIRELY in fluent, sophisticated, professional Arabic.
- If the user asks in English, reply in English.
- Ground your answers in the PROVIDED REAL ESTATE CONTEXT. Always reference specific project titles, locations, luxury brand partners, amenities, and pricing details when available.
- If the user asks about domestic Saudi properties or local listings in Riyadh/Jeddah, highlight Wasalt verified properties.
- If the user asks about international branded residences or trophy assets, highlight DarGlobal developments.
- Provide official listing links when available so users can explore and book viewings.
- Tone: Sophisticated, courteous, authoritative, and direct.
"""

def clean_model_output(text: str) -> str:
    """
    Cleans any residual chain-of-thought, <think> tags, or model self-notes.
    """
    if not text:
        return ""
    
    # Strip <think>...</think> tags if present
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # If a model output internal reasoning monologue before Arabic response:
    if "The user is asking" in text or "Key points from guidelines" in text or "So for Riyadh luxury" in text:
        # Search for Arabic response starting point
        ar_match = re.search(r'([\u0600-\u06FF][^\n]*\n.*)', text, flags=re.DOTALL)
        if ar_match:
            return ar_match.group(1).strip()
        # If no Arabic, search for final markdown heading or conclusion
        sections = re.split(r'\n(?=#{1,3}\s|\*\*|\bHere\b|\bWelcome\b)', text)
        if len(sections) > 1:
            return "\n".join(sections[1:]).strip()
            
    return text.strip()

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
                "temperature": 0.3
            }
            
            try:
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=18) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choices = data.get("choices", [])
                    if choices:
                        msg = choices[0].get("message", {})
                        content = msg.get("content") or choices[0].get("text") or ""
                        
                        # Clean any model monologue or thinking tags
                        cleaned = clean_model_output(content)
                        if cleaned:
                            model_used = data.get("model", model)
                            return {
                                "reply": cleaned,
                                "model_used": model_used,
                                "status": "success"
                            }
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8", errors="ignore")
                logger.info(f"[Auto-Failover] Model {model} with Key #{key_idx+1} reached quota/limit ({e.code}). Cascading to next free model...")
                last_error = f"HTTP {e.code}: {err_text[:80]}"
                continue # Try next key or next model
            except Exception as e:
                logger.info(f"[Auto-Failover] Model {model} with Key #{key_idx+1} retry: {e}")
                last_error = str(e)
                continue

    # Graceful fallback advisory response based on context
    logger.error(f"All free models exhausted. Last error: {last_error}")
    return {
        "reply": (
            "I am currently experiencing high network demand on the inference gateway. "
            "However, based on our verified portfolio records:\n\n"
            + (context if context else "Please browse our highlighted projects below or try again in a few moments.")
        ),
        "model_used": "verified-portfolio-cache",
        "status": "fallback"
    }
