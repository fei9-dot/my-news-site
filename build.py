import feedparser
import os
import re
from datetime import datetime

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def fetch_rss(url):
    return feedparser.parse(url, agent=USER_AGENT)

def get_image(entry):
    # 嘗試從 summary 或 content 中提取圖片網址
    img_search = re.search(r'<img src="(.*?)"', entry.get('summary', ''))
    if img_search: return img_search.group(1)
    if 'media_content' in entry: return entry.media_content[0]['url']
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''): return link.href
    return "https://via.placeholder.com/400x200?text=News+Update"

def generate_html():
    # 1. 抓取多個優質來源
    sources = {
        "google": fetch_rss("https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"),
        "hket": fetch_rss("https://www.hket.com/rss/hongkong"),
        "unwire": fetch_rss("https://unwire.hk/feed/"),
        "bbc": fetch_rss("https://feeds.bbci.co.uk/news/world/asia/rss.xml")
    }

    # 2. 定義分類與黑名單
    BLACKLIST = ['加息', '恒指', '港股', '匯率', '強積金', '定存', '保險', '減息']
    
    # 初始化子欄位
    sub_cols = {"個股監控": [], "科技趨勢": [], "全球焦點": []}
    
    # 3. 處理與分流新聞 (左側大欄)
    # 個股監控：專攻 VOO, AMD, TTWO, NVDA 等
    for entry in sources['google'].entries + sources['hket'].entries:
        t = entry.title.upper()
        if any(b in t for b in BLACKLIST): continue
        
        if any(k in t for k in ['VOO', 'AMD', 'TTWO', 'NVDA', 'TESLA', 'GTA']):
            sub_cols["個股監控"].append(entry)
        elif any(k in t for k in ['AI', '晶片', '半導體', '遊戲', 'STARTUP', '創業']):
            sub_cols["科技趨勢"].append(entry)

    # 全球焦點 (放 BBC 內容)
    sub_cols["全球焦點"] = [e for e in sources['bbc'].entries if not any(b in e.title for b in BLACKLIST)]

    # 4. 生成 HTML 結構
    # 左側子欄位生成
    news_html = ""
    for title, entries in sub_cols.items():
        items = ""
        for e in entries[:8]:
            img = get_image(e)
            items += f'''
            <div class="card">
                <img src="{img}">
                <div class="card-body"><a href="{e.link}" target="_blank">{e.title}</a></div>
            </div>'''
        news_html += f'<div class="sub-col"><h3>{title}</h3>{items}</div>'

    # 右側熱話生成
    hot_html = "".join([f'<div class="card"><div class="card-body"><a href="{e.link}" target="_blank">{e.title}</a></div></div>' for e in sources['unwire'].entries[:12]])

    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>我的全屏資訊看板</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #f4f7f9; margin: 0; padding: 15px; }}
            h1 {{ text-align: center; color: #1a202c; margin-bottom: 25px; font-size: 28px; }}
            .last-update {{ text-align: center; color: #718096; font-size: 14px; margin-top: -20px; margin-bottom: 30px; }}
            
            /* 全屏布局 */
            .main-wrapper {{ display: flex; gap: 20px; width: 100%; }}
            
            /* 左側大欄 */
            .news-section {{ flex: 3; background: #fff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .news-grid {{ display: flex; gap: 15px; }}
            .sub-col {{ flex: 1; min-width: 0; }}
            
            /* 右側側邊欄 */
            .sidebar {{ flex: 1; background: #fff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            
            h2, h3 {{ color: #2d3748; border-bottom: 3px solid #4299e1; padding-bottom: 8px; }}
            h3 {{ font-size: 1.1rem; border-color: #bee3f8; }}
            
            .card {{ background: white; border: 1px solid #edf2f7; border-radius: 10px; margin-bottom: 15px; overflow: hidden; transition: 0.3s; }}
            .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 15px rgba(0,0,0,0.1); }}
            .card img {{ width: 100%; height: 140px; object-fit: cover; background: #e2e8f0; }}
            .card-body {{ padding: 12px; font-size: 14px; font-weight: 500; line-height: 1.5; }}
            .card-body a {{ text-decoration: none; color: #2d3748; }}
            
            @media (max-width: 1200px) {{ .news-grid, .main-wrapper {{ flex-direction: column; }} }}
        </style>
    </head>
    <body>
        <h1>🗞 我的個人化資訊監控看板</h1>
        <p class="last-update">最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="main-wrapper">
            <div class="news-section">
                <h2>🗞 新聞總覽</h2>
                <div class="news-grid">{news_html}</div>
            </div>
            <div class="sidebar">
                <h2>🔥 網上熱話</h2>
                {hot_html}
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    generate_html()
