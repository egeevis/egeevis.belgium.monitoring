import feedparser
import json
import datetime

FEEDS = {
    "nuclear": [
        {"name": "Google News (EN) — Nuclear Belgium",        "url": "https://news.google.com/rss/search?q=nuclear+Belgium+Doel+Tihange+FANC&hl=en&gl=BE&ceid=BE:en"},
        {"name": "Google News (FR) — Nucléaire Belgique",     "url": "https://news.google.com/rss/search?q=nucl%C3%A9aire+Belgique+Doel+Tihange&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (NL) — Kernenergie België",     "url": "https://news.google.com/rss/search?q=kernenergie+Belgi%C3%AB+Doel+Tihange&hl=nl&gl=BE&ceid=BE:nl"},
    ],
    "airspace": [
        {"name": "Google News (EN) — Belgium airspace",       "url": "https://news.google.com/rss/search?q=Belgium+airspace+aviation+military+Brussels&hl=en&gl=BE&ceid=BE:en"},
        {"name": "Google News (FR) — Espace aérien Belgique", "url": "https://news.google.com/rss/search?q=espace+a%C3%A9rien+Belgique+aviation&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (FR) — Drone Kleine-Brogel",    "url": "https://news.google.com/rss/search?q=Belgique+drone+espace+a%C3%A9rien+Kleine-Brogel&hl=fr&gl=BE&ceid=BE:fr"},
    ],
    "officials": [
        {"name": "Google News (FR) — De Wever premier",       "url": "https://news.google.com/rss/search?q=De+Wever+premier+Belgique+d%C3%A9claration&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (FR) — Lahbib affaires étrang.","url": "https://news.google.com/rss/search?q=Lahbib+affaires+%C3%A9trang%C3%A8res+Belgique&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (FR) — Francken défense",       "url": "https://news.google.com/rss/search?q=Francken+ministre+d%C3%A9fense+Belgique&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (EN) — Belgium government",     "url": "https://news.google.com/rss/search?q=Belgium+prime+minister+defence+foreign+minister+statement&hl=en&gl=BE&ceid=BE:en"},
    ],
    "parliament": [
        {"name": "Google News (FR) — Chambre fédérale",       "url": "https://news.google.com/rss/search?q=Chambre+repr%C3%A9sentants+Belgique+vote+loi&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (FR) — Parlement wallon",       "url": "https://news.google.com/rss/search?q=parlement+wallon+r%C3%A9solution+d%C3%A9cret&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (NL) — Vlaams Parlement",       "url": "https://news.google.com/rss/search?q=Vlaams+Parlement+decreet+stemming&hl=nl&gl=BE&ceid=BE:nl"},
        {"name": "Google News (FR) — Parlement bruxellois",   "url": "https://news.google.com/rss/search?q=parlement+bruxellois+ordonnance+vote&hl=fr&gl=BE&ceid=BE:fr"},
        {"name": "Google News (NL) — Europees Parlement/BE",  "url": "https://news.google.com/rss/search?q=Europees+Parlement+Belgi%C3%AB+Europarlementariers&hl=nl&gl=BE&ceid=BE:nl"},
    ],
}

result = {}
headers = {"User-Agent": "Mozilla/5.0 (compatible; RSS reader)"}

for cat, feeds in FEEDS.items():
    result[cat] = {}
    for feed in feeds:
        try:
            f = feedparser.parse(feed["url"], request_headers=headers)
            items = []
            for entry in f.entries[:8]:
                items.append({
                    "title":   entry.get("title", ""),
                    "link":    entry.get("link", "#"),
                    "date":    entry.get("published", ""),
                    "source":  entry.get("source", {}).get("title", "") if hasattr(entry.get("source", {}), "get") else "",
                })
            if items:
                result[cat][feed["name"]] = items
                print(f"✓ {feed['name']}: {len(items)} haber")
            else:
                print(f"✗ {feed['name']}: sonuç yok")
        except Exception as e:
            print(f"✗ {feed['name']}: hata — {e}")

output = {
    "updated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "data": result
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\ndata.json kaydedildi — {datetime.datetime.utcnow().isoformat()}")
