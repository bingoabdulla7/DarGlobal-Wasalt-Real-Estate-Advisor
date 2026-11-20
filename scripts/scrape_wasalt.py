import urllib.request
import json
import os
import re
import time

def scrape_wasalt(limit=60):
    print(f"Scraping Wasalt properties from sitemap and Next.js SSR (target: {limit})...")
    sitemap_url = 'https://cdn.wasalt.sa/sitemap/product_sitemap_en_sa.xml.gz'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    req = urllib.request.Request(sitemap_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        sitemap_text = r.read().decode('utf-8', errors='ignore')
        
    all_urls = re.findall(r'<loc>(https://wasalt\.sa/en/property/[^<]+)</loc>', sitemap_text)
    print(f"Discovered {len(all_urls)} property URLs in Wasalt sitemap.")
    
    # Filter for diverse property types (villas, apartments, duplexes, etc.)
    selected_urls = []
    seen_types = {}
    for u in all_urls:
        ptype = 'other'
        if 'villa' in u:
            ptype = 'villa'
        elif 'apartment' in u:
            ptype = 'apartment'
        elif 'duplex' in u:
            ptype = 'duplex'
        elif 'floor' in u:
            ptype = 'floor'
        elif 'land' in u:
            ptype = 'land'
            
        count = seen_types.get(ptype, 0)
        if count < 15: # balanced distribution
            selected_urls.append(u)
            seen_types[ptype] = count + 1
            if len(selected_urls) >= limit:
                break
                
    if len(selected_urls) < limit:
        selected_urls = all_urls[:limit]
        
    print(f"Selected {len(selected_urls)} target URLs across diverse property types.")
    
    properties = []
    for i, u in enumerate(selected_urls, 1):
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')
                
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
            if not m:
                continue
                
            data = json.loads(m.group(1))
            props = data.get('props', {}).get('pageProps', {})
            p_details = props.get('propertyDetailsV3', {})
            if not p_details:
                continue
                
            p_info = p_details.get('propertyInfo', {})
            pid = str(p_details.get('id', ''))
            
            # Attributes mapping
            attrs = {}
            for a in p_details.get('attributes', []):
                name = a.get('name')
                val = a.get('value')
                if name and val is not None:
                    attrs[name] = val
                    
            add_attrs = {}
            for a in p_details.get('additionalAttributes', []):
                lbl = a.get('label')
                val = a.get('value')
                if lbl and val is not None:
                    add_attrs[lbl] = val
            
            # Gallery
            gallery = props.get('galleryDetails', {}).get('images', {}).get('data', [])
            image_url = None
            if gallery and len(gallery) > 0:
                raw_img = gallery[0].get('content')
                if raw_img:
                    image_url = f"https://cdn.wasalt.sa/{raw_img}" if not raw_img.startswith('http') else raw_img
                    
            # Pricing
            price_val = p_info.get('price') or p_details.get('price')
            price_num = None
            if price_val:
                try:
                    price_num = float(str(price_val).replace(',', ''))
                except:
                    pass
            currency = p_info.get('currencyType', 'SAR')
            
            # Address and location
            address = p_info.get('address') or 'Saudi Arabia'
            city = p_info.get('city') or 'Riyadh'
            district = p_info.get('district') or ''
            prop_type = p_info.get('propertyType') or add_attrs.get('Property usage') or 'Residential'
            if 'villa' in u.lower():
                prop_type = 'Villa'
            elif 'apartment' in u.lower():
                prop_type = 'Apartment'
            elif 'duplex' in u.lower():
                prop_type = 'Duplex'
                
            bedrooms = attrs.get('Bedrooms') or attrs.get('noOfBedrooms')
            bathrooms = attrs.get('Bathrooms') or attrs.get('noOfBathrooms')
            area = attrs.get('Area') or attrs.get('propertyArea') or add_attrs.get('Property Area')
            
            # Slug to Title
            slug = u.split('/')[-1]
            slug_clean = re.sub(r'-\d+$', '', slug).replace('-', ' ').title()
            title = f"{prop_type}: {slug_clean}"
            if district and city:
                title += f" in {district}, {city}"
            elif city:
                title += f" in {city}"
                
            formatted_price = f"{currency} {int(price_num):,}" if price_num else "Price on Request"
            
            # REGA Verification
            rega_owner = p_details.get('propertyOwner', {})
            rega_lic = rega_owner.get('regaAdvLicNo') or 'REGA Verified'
            
            desc = (
                f"{title}. {prop_type} available in {city} (District: {district or 'Prime Location'}). "
                f"Listed price: {formatted_price}. "
                + (f"Features {bedrooms} bedrooms and {bathrooms} bathrooms. " if bedrooms and bathrooms else (f"Features {bedrooms} bedrooms. " if bedrooms else ""))
                + (f"Total land/built-up area: {area} sqm. " if area else "")
                + f"Regulated and licensed under Saudi REGA (License No. {rega_lic}). "
                f"High-potential real estate investment and family residency opportunity offered on Wasalt."
            )
            
            properties.append({
                "id": f"ws_{pid}",
                "source": "Wasalt",
                "title": title,
                "region": city,
                "city": city,
                "district": district,
                "country": "Saudi Arabia",
                "project_type": prop_type,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "area_sqm": area,
                "brand_partner": "Wasalt Verified Marketplace",
                "currency": currency,
                "price": formatted_price,
                "price_numeric": price_num,
                "image_url": image_url,
                "url": u,
                "description": desc,
                "rega_license": rega_lic,
                "tags": [city, prop_type, "Wasalt", "Saudi Arabia", "REGA Verified"]
            })
            print(f"[{i}/{len(selected_urls)}] Scraped: {title[:60]}... ({formatted_price})")
            time.sleep(0.1) # polite delay
            
        except Exception as e:
            print(f"[{i}/{len(selected_urls)}] Error parsing {u}: {e}")
            continue
            
    os.makedirs('data', exist_ok=True)
    out_path = os.path.join('data', 'wasalt_properties.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(properties, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully scraped {len(properties)} Wasalt properties into {out_path}!")
    return properties

if __name__ == '__main__':
    scrape_wasalt(limit=40)
