import datetime
import json
import re
from email.utils import parsedate_to_datetime

import feedparser

MAX_ITEMS_PER_FEED = 12

FEEDS = {
    "nuclear": [
        {
            "name": "Belga/Google News - Nukleer",
            "url": "https://news.google.com/rss/search?q=Belgium+nuclear+Doel+Tihange+FANC+Engie+Electrabel&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "Google News FR - Nucleaire Belgique",
            "url": "https://news.google.com/rss/search?q=nucleaire+Belgique+Doel+Tihange+prolongation&hl=fr&gl=BE&ceid=BE:fr",
        },
        {
            "name": "Google News NL - Kernenergie Belgie",
            "url": "https://news.google.com/rss/search?q=kernenergie+Belgie+Doel+Tihange+FANC&hl=nl&gl=BE&ceid=BE:nl",
        },
    ],
    "airspace": [
        {
            "name": "Google News EN - Belgium airspace",
            "url": "https://news.google.com/rss/search?q=Belgium+airspace+Brussels+ATC+NOTAM+military+exercise&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "Google News FR - Espace aerien",
            "url": "https://news.google.com/rss/search?q=espace+aerien+Belgique+Bruxelles+NOTAM+drone&hl=fr&gl=BE&ceid=BE:fr",
        },
        {
            "name": "Google News NL - Luchtruim",
            "url": "https://news.google.com/rss/search?q=Belgisch+luchtruim+Brussel+militair+oefening&hl=nl&gl=BE&ceid=BE:nl",
        },
    ],
    "officials": [
        {
            "name": "Basbakan - De Wever",
            "url": "https://news.google.com/rss/search?q=Bart+De+Wever+Belgium+prime+minister+statement&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "Disisleri - Lahbib",
            "url": "https://news.google.com/rss/search?q=Hadja+Lahbib+Belgium+foreign+minister+statement&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "Savunma - Francken",
            "url": "https://news.google.com/rss/search?q=Theo+Francken+Belgium+defence+minister+statement&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "Sosyal Medya - De Wever",
            "url": "https://news.google.com/rss/search?q=Bart+De+Wever+X+post+OR+tweet&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "Sosyal Medya - Lahbib",
            "url": "https://news.google.com/rss/search?q=Hadja+Lahbib+X+post+OR+tweet&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "Sosyal Medya - Francken",
            "url": "https://news.google.com/rss/search?q=Theo+Francken+X+post+OR+tweet&hl=en&gl=BE&ceid=BE:en",
        },
    ],
    "parliament": [
        {
            "name": "1) Federal Chamber",
            "url": "https://news.google.com/rss/search?q=Chamber+of+Representatives+Belgium+bill+proposal+vote&hl=en&gl=BE&ceid=BE:en",
        },
        {
            "name": "2) Flemish Parliament",
            "url": "https://news.google.com/rss/search?q=Vlaams+Parlement+decreet+voorstel+stemming&hl=nl&gl=BE&ceid=BE:nl",
        },
        {
            "name": "3) Walloon Parliament",
            "url": "https://news.google.com/rss/search?q=Parlement+wallon+projet+decret+vote&hl=fr&gl=BE&ceid=BE:fr",
        },
        {
            "name": "4) Brussels Parliament",
            "url": "https://news.google.com/rss/search?q=Parlement+bruxellois+ordonnance+proposition+vote&hl=fr&gl=BE&ceid=BE:fr",
        },
        {
            "name": "5) French Community Parliament",
            "url": "https://news.google.com/rss/search?q=Parlement+de+la+Federation+Wallonie+Bruxelles+proposition+decret&hl=fr&gl=BE&ceid=BE:fr",
        },
        {
            "name": "6) German-speaking Community",
            "url": "https://news.google.com/rss/search?q=Parlament+der+Deutschsprachigen+Gemeinschaft+Belgien+Dekret+Vorschlag&hl=de&gl=BE&ceid=BE:de",
        },
    ],
}


def to_iso_date(entry):
    for key in ("published_parsed", "updated_parsed"):
        if entry.get(key):
            dt = datetime.datetime(*entry[key][:6], tzinfo=datetime.timezone.utc)
            return dt.isoformat().replace("+00:00", "Z")

    for key in ("published", "updated"):
        raw = entry.get(key)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                return dt.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
            except Exception:
                continue

    return None


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*[-|:]\s*\S+$", "", text)
    return text


def build_summary(title, category):
    title = clean_text(title)
    if not title:
        return "Ozet uretilmedi."

    t = title.lower()

    if category == "parliament":
        if any(k in t for k in ["vote", "voted", "stemming", "adopt", "approve", "approuve", "adopte"]):
            return "Karar tasarisi oylama/nihai karar asamasina iliskin bir gelisme bildiriliyor."
        if any(k in t for k in ["proposal", "proposition", "voorstel", "bill", "decree", "decret", "dekret"]):
            return "Yeni bir tasari/teklif veya mevcut tasarinin ilerleyis adimi aktariliyor."
        return "Parlamento gundeminde bir tasari, karar veya komisyon surecine dair gelisme."

    if category == "officials":
        return "Basbakan veya ilgili bakanliklara ait aciklama ya da sosyal medya kaynakli siyasi guvenlik dis politika haberi."

    if category == "nuclear":
        return "Belcika nukleer santralleri, duzenleyici kurumlar veya enerji politikasi baglaminda bir guncelleme."

    if category == "airspace":
        return "Belcika hava sahasi, havacilik guvenligi, NOTAM veya askeri hava faaliyetleriyle ilgili bir gelisme."

    return "Konuya iliskin guncel bir gelisme bildiriliyor."


def parse_feed(name, url, category):
    parsed = feedparser.parse(url)
    if parsed.bozo and not parsed.entries:
        raise RuntimeError(f"Feed parse hatasi: {parsed.bozo_exception}")

    items = []
    for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
        title = clean_text(entry.get("title", ""))
        link = entry.get("link", "")
        if not title or not link:
            continue

        source_name = ""
        source_obj = entry.get("source") or {}
        if isinstance(source_obj, dict):
            source_name = source_obj.get("title", "")

        iso_date = to_iso_date(entry)
        items.append(
            {
                "title": title,
                "summary": build_summary(title, category),
                "link": link,
                "date": iso_date,
                "source": source_name,
                "feed": name,
            }
        )

    items.sort(key=lambda x: x.get("date") or "", reverse=True)
    return items


def dedupe(items):
    seen = set()
    out = []
    for item in items:
        key = (item.get("title", "").lower(), item.get("link", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def sort_by_date_desc(items):
    return sorted(items, key=lambda x: x.get("date") or "", reverse=True)


result = {}

for category, feeds in FEEDS.items():
    result[category] = {}
    for feed in feeds:
        name = feed["name"]
        url = feed["url"]
        try:
            items = parse_feed(name, url, category)
            if items:
                result[category][name] = items
                print(f"[OK] {name}: {len(items)}")
            else:
                print(f"[NO] {name}: sonuc yok")
        except Exception as exc:
            print(f"[ER] {name}: {exc}")

    merged = []
    for batch in result[category].values():
        merged.extend(batch)
    merged = sort_by_date_desc(merged)
    merged = dedupe(merged)
    merged = sort_by_date_desc(merged)
    result[category]["Toplu (Tekrarsiz)"] = merged[:40]

output = {
    "updated": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
    "meta": {
        "refresh": "30m",
        "notes": [
            "Parlamento kategorisi Belcika'nin 6 farkli parlamentosu icin ayri akislari kapsar.",
            "Ozet alanlari otomatik uretilir; resmi metinlerin birebir yerine hizli durum izleme amacli kullanin.",
        ],
    },
    "data": result,
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("data.json guncellendi")
