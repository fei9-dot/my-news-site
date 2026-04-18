import feedparser
import re
from datetime import datetime

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def fetch_rss(url):
    return feedparser.parse(url, agent=USER_AGENT)

def generate_html():
    # --- 核心情報源：主動搜尋 (這會大幅增加資訊量) ---
    # 我們不再只抓一個 RSS，而是把搜尋範圍擴大
    search_queries = {
        "個股": "AMD+OR+VOO+OR+TTWO+OR+NVDA+OR+NASDAQ+stock",
        "科技": "AI+晶片+OR+半導體+OR+智慧農業+OR+創業+Startup",
        "收藏": "Pokemon+Card+OR+PTCG+OR+CS2+skins+market"
    }

    sub_cols = {"📊 個股 & 財經": [], "🤖 科技 & 創業": [], "🌎 全球焦點": []}
    BLACKLIST = ['加息', '恒指', '港股', '匯率', '強積金', '定期存款']

    # 1. 抓取搜尋結果
    for cat, query in search_queries.items():
        url = f"https://news.google.com/rss/search?q={query}&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        feed = fetch_rss(url)
        # 根據分類塞進對應的欄位
        if cat == "個股":
            sub_cols["📊 個股 & 財經"] = [e for e in feed.entries if not any(b in e.title for b in BLACKLIST)]
        elif cat == "科技":
            sub_cols["🤖 科技 & 創業"] = [e for e in feed.entries if not any(b in e.title for b in BLACKLIST)]

    # 2. 抓取全球即時新聞 (使用 Google Top Stories)
    global_feed = fetch_rss("https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant")
    sub_cols["🌎 全球焦點"] = [e for e in global_feed.entries if not any(b in e.title for b in BLACKLIST)]

    # 3. 處理熱話 (側邊欄)
    unwire = fetch_rss("https://unwire.hk/feed/")
    hot_items = unwire.entries[:20] # 增加熱話數量

    # --- HTML 渲染 ---
    news_html = ""
    for title, entries in sub_cols.items():
        # 增加每欄顯示數量到 18 條，讓你一次看個夠
        items = "".join([f'<div class="item"><span class="time">{e.get("published", "")[5:16]}</span><br><a href="{e.link}" target="_blank">{e.title}</a></div>' for e in entries[:18]])
        news_html += f'<div class="sub-col"><h3>{title}</h3>{items}</div>'

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>我的情報監控中心</title>
        <style>
            body {{ font-family: "Segoe UI", sans-serif; background: #1a202c; color: #e2e8f0; margin: 0; padding: 20px; }}
            .container {{ display: flex; gap: 20px; }}
            .main {{ flex: 4; display: flex; gap: 15px; }}
            .sub-col {{ flex: 1; background: #2d3748; padding: 15px; border-radius: 10px; }}
            .side {{ flex: 1; background: #2d3748; padding: 15px; border-radius: 10px; font-size: 0.9em; }}
            
            h3 {{ color: #63b3ed; border-bottom: 2px solid #4a5568; padding-bottom: 10px; margin-top: 0; }}
            .item {{ margin-bottom: 15px; border-bottom: 1px solid #4a5568; padding-bottom: 8px; }}
            .time {{ font-size: 0.75em; color: #a0aec0; }}
            a {{ text-decoration: none; color: #fff; line-height: 1.4; display: inline-block; }}
            a:hover {{ color: #63b3ed; }}
            
            /* 針對全屏優化：滾動條樣式 */
            ::-webkit-scrollbar {{ width: 6px; }}
            ::-webkit-scrollbar-thumb {{ background: #4a5568; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <h2 style="margin-bottom:20px;">🕵️‍♂️ 每日情報總覽 <span style="font-size:0.5em; color:#a0aec0;">更新時間: {datetime.now().strftime('%H:%M:%S')}</span></h2>
        <div class="container">
            <div class="main">{news_html}</div>
            <div class="side">
                <h3 style="color:#f6ad55;">🔥 科技熱話</h3>
                {"".join([f'<div class="item"><a href="{e.link}" target="_blank">{e.title}</a></div>' for e in hot_items])}
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    generate_html()
