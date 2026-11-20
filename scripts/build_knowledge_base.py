import json
import os
import re

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', str(text))
    return text.strip()

def build_knowledge_base():
    print("Building unified knowledge base from DarGlobal and Wasalt...")
    
    dg_path = os.path.join('data', 'darglobal_projects.json')
    ws_path = os.path.join('data', 'wasalt_properties.json')
    
    darglobal_items = []
    wasalt_items = []
    
    if os.path.exists(dg_path):
        with open(dg_path, 'r', encoding='utf-8') as f:
            darglobal_items = json.load(f)
            
    if os.path.exists(ws_path):
        with open(ws_path, 'r', encoding='utf-8') as f:
            wasalt_items = json.load(f)
            
    print(f"Loaded {len(darglobal_items)} DarGlobal projects and {len(wasalt_items)} Wasalt properties.")
    
    # Enrich with foundational company profiles & FAQs for deep RAG knowledge
    company_profiles = [
        {
            "id": "info_dg_about",
            "source": "DarGlobal",
            "title": "About DarGlobal — International Luxury Real Estate Developer",
            "region": "International",
            "location": "London, UK (Headquarters); Dubai, UAE; Riyadh, KSA",
            "country": "International",
            "project_type": "Corporate Profile & Investment Overview",
            "bedrooms": None,
            "completion_date": None,
            "brand_partner": "DarGlobal",
            "currency": "USD",
            "price": "N/A",
            "price_numeric": None,
            "image_url": "https://cdn.darglobal.co.uk/TTD_exterior_02_bd7d425e3c.webp",
            "url": "https://darglobal.co.uk/about-us",
            "description": (
                "DarGlobal (LSE: DAR) is the premier international luxury real estate development company, "
                "originally founded as the international arm of Dar Al Arkan (Saudi Arabia's premier developer). "
                "Listed on the London Stock Exchange, DarGlobal specializes in high-end, design-led second homes, "
                "branded luxury residences, and hospitality destinations across prime global locations including "
                "the United Arab Emirates (Dubai, Ras Al Khaimah), the United Kingdom (central London), Spain (Marbella, Benahavís), "
                "Oman (AIDA cliffside community), Qatar (Simaisma, Doha), and Saudi Arabia (Wadi Safar Riyadh, Jeddah). "
                "DarGlobal is renowned for its world-class collaborations with elite brands including The Trump Organization, "
                "Automobili Lamborghini, Pagani Automobili, Aston Martin, Elie Saab, Missoni, Mouawad, and Marriott/W Hotels."
            ),
            "tags": ["DarGlobal", "Corporate Profile", "Luxury Real Estate", "LSE: DAR", "Dar Al Arkan"]
        },
        {
            "id": "info_ws_about",
            "source": "Wasalt",
            "title": "About Wasalt — Leading Saudi Arabian Real Estate Marketplace",
            "region": "Saudi Arabia",
            "location": "Riyadh, Saudi Arabia",
            "country": "Saudi Arabia",
            "project_type": "Marketplace Profile & Saudi Regulations",
            "bedrooms": None,
            "completion_date": None,
            "brand_partner": "Wasalt",
            "currency": "SAR",
            "price": "N/A",
            "price_numeric": None,
            "image_url": "https://assets.wasalt.com/others/icons/riyadh.svg",
            "url": "https://wasalt.sa/en",
            "description": (
                "Wasalt is a premier digital real estate marketplace in the Kingdom of Saudi Arabia, backed by Dar Al Arkan. "
                "Wasalt offers a comprehensive platform for finding, buying, renting, and investing in residential and commercial "
                "properties throughout Saudi Arabia, including Riyadh, Jeddah, Dammam, Al Khobar, Mecca, and Medina. "
                "All listings on Wasalt are licensed and strictly regulated under Saudi Arabia's Real Estate General Authority (REGA), "
                "ensuring transparent legal compliance, advertising licensing numbers, verified ownership, and safe transactions aligned with Saudi Vision 2030."
            ),
            "tags": ["Wasalt", "Saudi Arabia", "Marketplace", "REGA", "Saudi Vision 2030", "Dar Al Arkan"]
        },
        {
            "id": "info_faq_comparison",
            "source": "Both",
            "title": "DarGlobal vs Wasalt — Complementary Real Estate Ecosystem",
            "region": "Global & Saudi Arabia",
            "location": "International & Saudi Arabia",
            "country": "International & Saudi Arabia",
            "project_type": "Buyer Guide & Investment Comparison",
            "bedrooms": None,
            "completion_date": None,
            "brand_partner": "Dar Al Arkan Ecosystem",
            "currency": "Multi-Currency",
            "price": "N/A",
            "price_numeric": None,
            "image_url": "https://cdn.darglobal.co.uk/TTD_exterior_02_bd7d425e3c.webp",
            "url": "https://darglobal.co.uk",
            "description": (
                "How DarGlobal and Wasalt work together: Both entities are part of the prestigious Dar Al Arkan real estate lineage. "
                "DarGlobal focuses on ultra-luxury international branded residences and trophy vacation investments across London, Dubai, Spain, Oman, and Qatar. "
                "Wasalt provides the definitive national portal for domestic Saudi Arabian real estate, offering thousands of verified residential villas, "
                "apartments, masterplans, and commercial properties in key Saudi metropolitan centers like Riyadh and Jeddah. "
                "Clients seeking global lifestyle trophies and branded luxury invest through DarGlobal, while clients seeking family homes, rentals, "
                "or domestic real estate in the Kingdom search through Wasalt."
            ),
            "tags": ["Comparison", "DarGlobal", "Wasalt", "Investment Strategy", "Dar Al Arkan"]
        }
    ]
    
    all_records = []
    
    # Process corporate records
    for item in company_profiles:
        all_records.append(item)
        
    # Process DarGlobal projects
    for item in darglobal_items:
        all_records.append(item)
        
    # Process Wasalt properties
    for item in wasalt_items:
        all_records.append(item)
        
    print(f"Total unified knowledge base records: {len(all_records)}")
    
    os.makedirs('data', exist_ok=True)
    out_kb_path = os.path.join('data', 'knowledge_base.json')
    with open(out_kb_path, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated unified knowledge base at {out_kb_path}!")
    return all_records

if __name__ == '__main__':
    build_knowledge_base()
