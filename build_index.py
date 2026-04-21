import os
import glob
from datetime import datetime

directory = "/data/.openclaw/workspace/ai-website"
os.chdir(directory)

# Get all main newsletters
main_files = glob.glob("*_uutiset_*.html") + glob.glob("executive_ai_brief_*.html") + glob.glob("viikon_ai_uutiset_*.html") + glob.glob("copilot_katsaus_*.html")
main_items = []
for f in main_files:
    if "hot_news" in f: continue
    parts = f.replace(".html", "").split("_")
    date_str = parts[-1]
    title = " ".join(parts[:-1]).capitalize().replace("-", " ")
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        main_items.append({"file": f, "date": dt, "title": title, "date_str": date_str})
    except:
        pass

main_items.sort(key=lambda x: x["date"], reverse=True)

# Get Hot News alerts (expecting format hot_news_YYYY-MM-DD_HHMMSS.html or hot_news_YYYY-MM-DD.html)
hot_files = glob.glob("hot_news_*.html")
hot_items = []
for f in hot_files:
    # Try to extract date and time if available
    base = f.replace(".html", "").replace("hot_news_", "")
    # could be YYYY-MM-DD_HHMMSS or YYYY-MM-DD
    date_part = base[:10]
    try:
        dt = datetime.strptime(date_part, "%Y-%m-%d")
        
        # Read the file to extract the actual headline for the link text
        headline = "Hot News -nosto"
        try:
            with open(f, "r", encoding="utf-8") as html_file:
                content = html_file.read()
                # Very simple extraction of the h1 or title
                if "<title>Hot News Alert</title>" in content and "<h1><a" in content:
                    import re
                    match = re.search(r'<h1><a[^>]*>(.*?)</a></h1>', content)
                    if match:
                        headline = match.group(1).strip()
        except:
            pass
            
        hot_items.append({"file": f, "date": dt, "title": headline, "sort_key": os.path.getmtime(f)})
    except Exception as e:
        pass

hot_items.sort(key=lambda x: x["sort_key"], reverse=True)

html_content = """<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-uutiskirjeet & Hot News</title>
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; background: #f4f4f0; color: #333; margin: 0; padding: 0; }
        .container { max-width: 1000px; margin: 40px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .header { background: #0d1b2a; color: white; padding: 30px 20px; border-radius: 8px 8px 0 0; margin: -20px -20px 20px -20px; text-align: center; }
        h1 { margin: 0; font-size: 28px; letter-spacing: 1px; }
        .header p { margin: 10px 0 0 0; color: #7db8e8; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
        .content-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
        @media (max-width: 768px) { .content-grid { grid-template-columns: 1fr; } }
        ul { list-style-type: none; padding: 0; }
        li { margin: 15px 0; padding: 20px; border: 1px solid #eee; border-left: 4px solid #2563c7; border-radius: 4px; transition: all 0.2s; background: #fafaf8; }
        li:hover { background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transform: translateX(2px); }
        
        /* Hot news specific styling */
        .hot-news-list li { border-left: 4px solid #dc2626; background: #fffcfc; padding: 15px; }
        .hot-news-list a { font-size: 15px; }
        .hot-news-list .tag { display: inline-block; background: #fef2f2; color: #dc2626; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; border: 1px solid #fecaca; margin-bottom: 5px; text-transform: uppercase; }
        
        a { text-decoration: none; color: #0d1b2a; font-size: 18px; font-weight: bold; display: block; }
        a:hover { color: #2563c7; }
        .date { font-size: 13px; color: #666; display: block; margin-top: 8px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Tekoälykatsaukset & Uutisnostot</h1>
            <p>Automatisoitu uutisvirta</p>
        </div>
        
        <div class="content-grid">
            <div class="main-column">
                <h2 style="margin-bottom: 20px; color: #444; border-bottom: 2px solid #eee; padding-bottom: 10px;">Säännölliset katsaukset</h2>
                <ul>
"""

for item in main_items:
    display_title = item["title"]
    if "Paivan ai" in display_title:
        display_title = "Päivän tärkeimmät AI-uutiset"
    elif "Telco ai" in display_title:
        display_title = "Telco-sektorin AI-uutiset"
    elif "Executive ai" in display_title:
        display_title = "Johdon tiivistelmä (Executive Brief)"
    elif "Viikon ai" in display_title:
        display_title = "Viikon tärkeimmät AI-uutiset"
    elif "Copilot katsaus" in display_title:
        display_title = "Microsoft Copilot - Käyttötapaukset"
        
    html_content += f"""                    <li>
                        <a href="{item['file']}">{display_title}</a>
                        <span class="date">{item['date'].strftime('%d.%m.%Y')}</span>
                    </li>\n"""

html_content += """                </ul>
            </div>
            <div class="sidebar-column">
                <h2 style="margin-bottom: 20px; color: #dc2626; border-bottom: 2px solid #fecaca; padding-bottom: 10px;">🔥 Hot News -nostot</h2>
                <ul class="hot-news-list">
"""

if not hot_items:
    html_content += "                    <li><p style='color: #666; font-size: 14px; margin: 0;'>Ei uusia nostoja.</p></li>\n"
else:
    for item in hot_items:
        html_content += f"""                    <li>
                        <span class="tag">HOT NEWS</span>
                        <a href="{item['file']}">{item['title']}</a>
                        <span class="date">{item['date'].strftime('%d.%m.%Y')}</span>
                    </li>\n"""

html_content += """                </ul>
            </div>
        </div>
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("index.html generated with Hot News section")
