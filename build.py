import feedparser

# 設定你的來源
news_sources = [
    {"title": "🛡️ 權威資訊", "url": "https://www.hket.com/rss/hongkong"},
    {"title": "🔥 網上熱話", "url": "https://www.reddit.com/r/hongkong/.rss"},
    {"title": "🎲 隨機頁面", "url": "https://news.google.com/rss?hl=zh-HK&gl=HK"}
]

html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>我的新聞站</title>
    <style>
        body {{ font-family: sans-serif; display: flex; gap: 20px; padding: 20px; background: #f5f5f5; }}
        .column {{ flex: 1; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h2 {{ border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        a {{ text-decoration: none; color: #1a73e8; display: block; margin-bottom: 10px; }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

columns_html = ""
for source in news_sources:
    feed = feedparser.parse(source['url'])
    items_html = ""
    # 只取前 10 條
    for entry in feed.entries[:10]:
        items_html += f'<a href="{entry.link}" target="_blank">{entry.title}</a>'
    
    columns_html += f'<div class="column"><h2>{source["title"]}</h2>{items_html}</div>'

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template.format(content=columns_html))