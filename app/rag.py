import json
import os
import re
from typing import List, Dict, Any, Optional

class KnowledgeRetriever:
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base.json')
        self.items: List[Dict[str, Any]] = []
        self.load_data()
        
    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.items = json.load(f)
        else:
            # Fallback to darglobal if kb not yet generated
            dg_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'darglobal_projects.json')
            if os.path.exists(dg_path):
                with open(dg_path, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
            else:
                self.items = []
                
    def reload(self):
        self.load_data()

    def search(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Performs hybrid keyword & attribute search over real estate knowledge base.
        Returns both prompt context and structured property cards for UI display.
        """
        if not self.items:
            self.load_data()
            if not self.items:
                return {"context": "No property database loaded.", "properties": []}

        q = query.lower()
        q_tokens = set(re.findall(r'\b\w+\b', q))
        # Remove common stopwords
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'for', 'of', 'and', 'or', 'is', 'to', 'with', 'me', 'what', 'are', 'show', 'tell', 'find', 'i', 'want', 'any'}
        q_tokens = [t for t in q_tokens if t not in stopwords and len(t) > 1]

        # Extract explicit constraints from query
        wants_darglobal = any(k in q for k in ['darglobal', 'dar global', 'dar al arkan', 'international', 'luxury', 'trump', 'lamborghini', 'pagani', 'missoni', 'elie saab', 'mouawad', 'spain', 'oman', 'london', 'qatar', 'dubai', 'rak'])
        wants_wasalt = any(k in q for k in ['wasalt', 'saudi', 'riyadh', 'jeddah', 'khobar', 'dammam', 'rega', 'sar', 'domestic'])

        scored_items = []
        for item in self.items:
            score = 0.0
            
            # Text fields
            title = (item.get('title') or '').lower()
            location = (item.get('location') or item.get('region') or '').lower()
            country = (item.get('country') or '').lower()
            brand = (item.get('brand_partner') or '').lower()
            ptype = (item.get('project_type') or '').lower()
            desc = (item.get('description') or '').lower()
            tags = " ".join(item.get('tags', [])).lower()
            source = (item.get('source') or '').lower()

            # Source preference booster
            if wants_darglobal and source == 'darglobal':
                score += 15.0
            if wants_wasalt and source == 'wasalt':
                score += 15.0

            # Direct full phrase or token matching
            for token in q_tokens:
                if token in title:
                    score += 10.0
                if token in brand:
                    score += 9.0
                if token in location or token in country:
                    score += 8.0
                if token in ptype:
                    score += 6.0
                if token in tags:
                    score += 5.0
                if token in desc:
                    score += 2.0

            # Special keyword boosters
            if 'villa' in q and 'villa' in ptype:
                score += 8.0
            if 'apartment' in q and ('apartment' in ptype or 'residence' in ptype):
                score += 8.0
            if 'trump' in q and 'trump' in brand:
                score += 25.0
            if 'lamborghini' in q and 'lamborghini' in brand:
                score += 25.0
            if 'pagani' in q and 'pagani' in brand:
                score += 25.0
            if 'oman' in q and 'oman' in location:
                score += 20.0
            if 'spain' in q and 'spain' in location:
                score += 20.0
            if 'dubai' in q and 'dubai' in location:
                score += 20.0
            if 'london' in q and 'london' in location:
                score += 20.0
            if 'riyadh' in q and 'riyadh' in location:
                score += 20.0
            if 'jeddah' in q and 'jeddah' in location:
                score += 20.0

            # Base priority for overview/comparison articles when query asks generally
            if any(term in q for term in ['about', 'who is', 'difference', 'compare', 'how', 'ecosystem', 'background']):
                if 'about' in item.get('id', '') or 'faq' in item.get('id', ''):
                    score += 30.0

            if score > 0:
                scored_items.append((score, item))

        # Sort descending by score
        scored_items.sort(key=lambda x: x[0], reverse=True)
        top_matches = [item for score, item in scored_items[:top_k]]

        # If no tokens matched, return top diverse sample items
        if not top_matches:
            top_matches = self.items[:top_k]

        # Format context for prompt
        context_chunks = []
        structured_properties = []

        for i, item in enumerate(top_matches, 1):
            source = item.get('source', 'DarGlobal')
            title = item.get('title')
            loc = item.get('location') or item.get('region')
            ptype = item.get('project_type')
            price = item.get('price', 'Price on Application')
            brand = item.get('brand_partner', 'DarGlobal')
            url = item.get('url', 'https://darglobal.co.uk')
            desc = item.get('description', '')
            img = item.get('image_url')
            comp = item.get('completion_date')
            beds = item.get('bedrooms')

            chunk = (
                f"[{i}] {title}\n"
                f"Source: {source}\n"
                f"Location: {loc}\n"
                f"Type: {ptype} | Brand: {brand}\n"
                f"Price: {price}"
                + (f" | Bedrooms: {beds}" if beds else "")
                + (f" | Delivery: {comp}" if comp else "")
                + f"\nListing URL: {url}\n"
                f"Summary: {desc}\n"
            )
            context_chunks.append(chunk)

            # Property card data for the frontend
            if not item.get('id', '').startswith('info_'):
                structured_properties.append({
                    "id": item.get('id'),
                    "title": title,
                    "source": source,
                    "location": loc,
                    "type": ptype,
                    "price": price,
                    "bedrooms": beds,
                    "brand": brand,
                    "url": url,
                    "image_url": img,
                    "completion": comp
                })

        return {
            "context": "\n".join(context_chunks),
            "properties": structured_properties[:4]
        }

retriever = KnowledgeRetriever()
