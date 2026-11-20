import urllib.request
import json
import os
import re

def scrape_darglobal():
    print("Fetching DarGlobal projects from Strapi CMS API...")
    url = 'https://strapi.darglobal.co.uk/api/projects?populate=Tabs'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        
    tabs = data.get('data', {}).get('attributes', {}).get('Tabs', [])
    projects = []
    
    brand_keywords = {
        'Trump': 'The Trump Organization',
        'Lamborghini': 'Automobili Lamborghini',
        'Aston Martin': 'Aston Martin',
        'Missoni': 'Missoni',
        'Elie Saab': 'Elie Saab',
        'Mouawad': 'Mouawad',
        'Pagani': 'Pagani Automobili',
        'Marriott': 'Marriott International',
        'W Residences': 'W Hotels / Marriott'
    }

    currency_by_region = {
        'United Arab Emirates': 'AED',
        'Spain': 'EUR',
        'Qatar': 'QAR',
        'Oman': 'OMR',
        'United Kingdom': 'GBP',
        'Saudi Arabia': 'SAR'
    }
    
    for tab in tabs:
        region = tab.get('TabHeading', 'International')
        tab_data = tab.get('TabData', [])
        default_currency = currency_by_region.get(region, 'USD')
        
        for item in tab_data:
            pid = item.get('id')
            title = (item.get('ProjectTitle') or '').strip()
            location = (item.get('Location') or '').strip()
            project_type = (item.get('ProjectType') or 'Luxury Residence').strip()
            completion_date = item.get('completionDate')
            bedrooms = item.get('Bedrooms')
            rel_link = item.get('Link') or ''
            full_link = f"https://darglobal.co.uk{rel_link}" if rel_link.startswith('/') else rel_link
            
            # Extract card image
            img_data = item.get('ProjectCardImage', {}).get('data')
            image_url = None
            if img_data and isinstance(img_data, dict):
                image_url = img_data.get('attributes', {}).get('url')
                
            # Detect brand partner
            brand_partner = "DarGlobal Signature"
            for kw, brand_name in brand_keywords.items():
                if kw.lower() in title.lower() or kw.lower() in location.lower():
                    brand_partner = brand_name
                    break
            
            # Generate rich descriptive text
            desc = (
                f"{title} is a premier luxury development by DarGlobal situated in {location} ({region}). "
                f"Featuring elite {project_type.lower()}"
                + (f" with {bedrooms} bedroom configurations" if bedrooms else "")
                + f", the project is created in partnership with {brand_partner}. "
                + (f"Scheduled for completion by {completion_date}. " if completion_date else "")
                + f"DarGlobal elevates upscale international living with world-class architecture, bespoke amenities, and prime investment appeal."
            )
            
            projects.append({
                "id": f"dg_{pid}",
                "source": "DarGlobal",
                "title": title,
                "region": region,
                "location": location,
                "country": region,
                "project_type": project_type,
                "bedrooms": bedrooms,
                "completion_date": completion_date,
                "brand_partner": brand_partner,
                "currency": default_currency,
                "price": "Price on Application",
                "price_numeric": None,
                "image_url": image_url,
                "url": full_link,
                "description": desc,
                "tags": [region, project_type, brand_partner, "DarGlobal", "Luxury Real Estate"]
            })
            
    os.makedirs('data', exist_ok=True)
    out_path = os.path.join('data', 'darglobal_projects.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully scraped {len(projects)} DarGlobal projects into {out_path}!")
    return projects

if __name__ == '__main__':
    scrape_darglobal()
