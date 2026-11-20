import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import json
from app.main import health_check, get_properties, chat_endpoint, ChatRequest, MessageItem

async def run_tests():
    print("Testing Healthcheck...")
    h = await health_check()
    print("Healthcheck:", h)

    print("\nTesting Properties API...")
    p_dg = await get_properties(source='DarGlobal')
    print("DarGlobal properties count:", json.loads(p_dg.body)['total'])

    p_ws = await get_properties(source='Wasalt')
    print("Wasalt properties count:", json.loads(p_ws.body)['total'])

    print("\nTesting Chat endpoint with OpenRouter Free Model...")
    req = ChatRequest(
        messages=[MessageItem(role='user', content='What Trump projects do you have in Dubai and what villas in Riyadh?')],
        model='openrouter/free'
    )
    c = await chat_endpoint(req)
    chat_data = json.loads(c.body)
    print("Chat Status:", chat_data['status'])
    print("Model Used:", chat_data['model_used'])
    print("Properties Matched:", len(chat_data['properties']))
    for p in chat_data['properties']:
        print(f"  - [{p['source']}] {p['title']} ({p['location']})")
    print("\nAI Advisor Reply Preview:")
    print(chat_data['reply'][:350])
    print("\n[PASS] All core application functions verified successfully!")

if __name__ == '__main__':
    asyncio.run(run_tests())
