import feedparser
import os
from datetime import datetime

# 加強抓取成功率：偽裝成一般瀏覽器
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def fetch_rss(url):
    return feedparser.parse(url, agent=USER_AGENT)

# 設定你的新聞來源
news_sources = {
    "trust": [
        {"name": "經濟日報 (HKET)", "url": "https://www.hket.com/rss/hongkong"},
        {"name": "BBC 中文網", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml"}
    ],
    "rumors": [
        {"name": "Unwire.hk", "url": "https://unwire.hk/feed/"},
        {"name": "Reddit Tech", "url": "https://www.reddit.com/r/technology/.rss"}
    ],
    "random": [
        {"name": "Google 新聞", "url": "https://news.google.com/rss?hl=zh-HK&gl=HK"}
    ]
}

def generate_html():
    columns_html = ""
    for col_title, sources in news_sources.items():
        # 中文化標題
        display_title = {"trust": "🛡️ 權威資訊", "rumors": "🔥 網上熱話", "random": "🎲 隨機頁面"}[col_title]
        
        source_content = ""
        for src in sources:
            feed = fetch_rss(src['url'])
            items = ""
            # 每個來源取 6 條新聞
            for entry in feed.entries[:6]:
                items += f'''
                <div style="margin-bottom:12px; border-bottom:1px solid #eee; padding-bottom:8px;">
                    <a href="{entry.link}" target="_blank" style="text-decoration:none; color:#1a73e8; font-weight:500;">{entry.title}</a>
                </div>'''
            source_content += f'<div style="margin-bottom:25px;"><h3 style="color:#555; font-size:0.9em;">{src["name"]}</h3>{items}</div>'
        
        columns_html += f'''
        <div style="flex:1; background:white; padding:20px; border-radius:10px; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="border-bottom:3px solid #0078d4; padding-bottom:10px;">{display_title}</h2>
            {source_content}
        </div>'''

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>我的資訊儀表板</title>
    </head>
    <body style="font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background:#f0f2f5; margin:0; padding:20px;">
        <div style="max-width:1200px; margin:0 auto;">
            <header style="text-align:center; margin-bottom:30px;">
                <h1 style="color:#1c1e21;">🗞 我的個人化資訊看板</h1>
                <p style="color:#65676b;">最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </header>
            <div style="display:flex; gap:20px; flex-wrap:wrap;">
                {columns_html}
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generate_html()
