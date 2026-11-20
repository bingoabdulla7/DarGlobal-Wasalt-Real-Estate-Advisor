import os
import re

def load_keys_from_env_file():
    keys = []
    # Check current directory and parent directory for .env
    env_paths = ['.env', os.path.join(os.path.dirname(__file__), '..', '.env')]
    for p in env_paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPENROUTER_API_KEY') and '=' in line:
                        val = line.split('=', 1)[1].strip().strip('"').strip("'")
                        if val and val not in keys:
                            keys.append(val)
    # Check OS environment variables
    env_key1 = os.environ.get('OPENROUTER_API_KEY')
    env_key2 = os.environ.get('OPENROUTER_API_KEY_FALLBACK') or os.environ.get('OPENROUTER_API_KEY_2')
    if env_key1 and env_key1 not in keys:
        keys.insert(0, env_key1)
    if env_key2 and env_key2 not in keys:
        keys.append(env_key2)
        
    return keys

API_KEYS = load_keys_from_env_file()

# STRICTLY FREE MODELS AVAILABLE ON OPENROUTER
# Priority order: highest quality instruction models first, followed by fast and reasoning models, with openrouter/free router
FREE_MODELS = [
    "openrouter/free",                                      # Auto-routes to best available free model
    "google/gemma-4-31b-it:free",                           # Top-tier 31B instruction model
    "google/gemma-4-26b-a4b-it:free",                       # Gemma 26B instruction model
    "nvidia/nemotron-3.5-lightning:free",                   # Fast Nvidia high-performance
    "nvidia/nemotron-3.5-super-vl:free",                    # Nvidia Super VL
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",  # Reasoning model
    "liquid/lfm-3-1.7b:free",                               # Lightweight Liquid model
    "dots-studio/dots-3-note-preview:free",                 # Dots Studio
    "baidu/ernie-5.5-flash-preview:free",                   # Baidu Ernie Flash
    "inclusionai/ling-3.2-flash:free",                      # InclusionAI Ling Flash
    "particle-ai/particle-1:free",                          # Particle-1
    "recursive/flint-v1.0:free"                             # Recursive Flint
]

DEFAULT_MODEL = "openrouter/free"
APP_TITLE = "DarGlobal & Wasalt Real Estate AI Advisor"
PORT = int(os.environ.get("PORT", 8000))
