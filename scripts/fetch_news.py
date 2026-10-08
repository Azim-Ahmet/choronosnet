import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
import re
import hashlib
import os

FEEDS = [
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "lang": "en", "default_cat": "jeopolitik"},
    {"url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "lang": "en", "default_cat": "bilim"},
    {"url": "https://feeds.bbci.co.uk/turkce/rss.xml", "lang": "tr", "default_cat": "jeopolitik"}
]

def clean_html(raw_html):
    clean = re.sub(r'<.*?>', '', raw_html)
    return clean.strip().replace('&quot;', '"').replace('&#39;', "'").replace('&amp;', '&')

def fetch_rss_items():
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ChronosNet/1.0"}
    for feed in FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall(".//item")[:5]:
                    title_elem = item.find("title")
                    desc_elem = item.find("description")
                    link_elem = item.find("link")
                    if title_elem is not None and title_elem.text:
                        items.append({
                            "title": clean_html(title_elem.text),
                            "desc": clean_html(desc_elem.text) if desc_elem is not None and desc_elem.text else clean_html(title_elem.text),
                            "link": link_elem.text if link_elem is not None else "",
                            "lang": feed["lang"],
                            "cat": feed["default_cat"]
                        })
        except Exception as e:
            print(f"Hata: {feed['url']} alinamadi: {e}")
    return items

def build_dossier(item):
    today = datetime.date.today().isoformat()
    now_time = datetime.datetime.now().strftime("%H:%M")
    h = hashlib.md5(item["title"].encode("utf-8")).hexdigest()[:8]
    slug = f"event-{today}-{h}"
    return {
        "id": slug,
        "category": item["cat"],
        "date": today,
        "views": 1200,
        "popularity": 89,
        "factStatus": "verified",
        "title": { "tr": item["title"], "en": item["title"] },
        "summary": { "tr": item["desc"], "en": item["desc"] },
        "timeline": [
            { "date": f"{today} {now_time}", "desc": f"Uluslararası ajanslar doğruladı: {item['title']}" }
        ],
        "background": "Gelişme küresel stratejik dengeler çerçevesinde uluslararası gözlemciler tarafından yakından izlenmektedir.",
        "related": f"• İlgili Haber Kaynağı: {item['link']}\n• Uluslararası Diplomatik Açıklamalar",
        "theories": [
            { "claim": "Olayın Görünmeyen Stratejik Nedenleri", "verdict": "Resmi incelemeler ve teyit süreçleri devam etmektedir." }
        ]
    }

def main():
    json_path = "dossiers.json"
    existing = []
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try: existing = json.load(f)
            except: existing = []
    
    existing_titles = {d.get("title", {}).get("tr", "").strip().lower() for d in existing}
    items = fetch_rss_items()
    added = 0
    for itm in items:
        if itm["title"].strip().lower() not in existing_titles:
            existing.insert(0, build_dossier(itm))
            existing_titles.add(itm["title"].strip().lower())
            added += 1
            if added >= 5: break
            
    existing = existing[:50]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"Tamamlandi! {added} yeni dosya eklendi.")

if __name__ == "__main__":
    main()
  
