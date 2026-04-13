# ==============================================================================
# run_campaign.py — 全自動推廣主控執行器 v3.0 (0成本最大收益版)
# 功能：AI生成獨特文案 -> 分潤連結 -> SEO最佳化HTML + Sitemap + 結構化資料
# 帳號：masatsai032@gmail.com / af000094185
# 0成本策略：Gemini免費額度 + GitHub Pages免費部署 + Windows排程自動化
# ==============================================================================

import os
import sys
import json
import random
import urllib.parse
import requests
from datetime import datetime
from dotenv import load_dotenv

# Windows cp950 終端機 emoji 相容修正
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GEMINI_API_KEY       = os.environ.get("GEMINI_API_KEY", "")
ICHANNELS_AFFILIATE_ID = os.environ.get("ICHANNELS_AFFILIATE_ID", "af000094185")
WEBHOOK_URL          = os.environ.get("WEBHOOK_URL", "")

CAMPAIGNS_FILE = os.path.join(BASE_DIR, "campaigns.json")
OUTPUT_DIR     = os.path.join(BASE_DIR, "output")
LOGS_DIR       = os.path.join(BASE_DIR, "logs")
HTML_FILE      = os.path.join(OUTPUT_DIR, "index.html")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR,   exist_ok=True)

# ── Gemini 初始化（有 Key 才啟用）──────────────────────────────────────────
ai_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "請填入您的_GEMINI_API_KEY":
    try:
        from google import genai
        from google.genai import types
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        print("[AI] ✅ Gemini AI 已就緒")
    except ImportError:
        print("[AI] ⚠️  google-genai 未安裝，請執行: pip install google-genai")
else:
    print("[AI] ℹ️  未設定 GEMINI_API_KEY，將使用內建備用文案範本")


# ── 核心函式 ─────────────────────────────────────────────────────────────────

def load_campaigns() -> list:
    with open(CAMPAIGNS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [c for c in data["campaigns"] if c.get("active")]


def make_affiliate_link(url: str, uid: str) -> str:
    """在原始 URL 追加 ic= 與 uid= 聯盟追蹤參數。"""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    params["ic"]  = [ICHANNELS_AFFILIATE_ID]
    params["uid"] = [uid]
    new_query = urllib.parse.urlencode(params, doseq=True)
    return urllib.parse.urlunparse((
        parsed.scheme, parsed.netloc, parsed.path,
        parsed.params, new_query, parsed.fragment
    ))


# 文案角度輪流，讓 Google 不認為重複內容（SEO重點）
_COPY_ANGLES = [
    "從使用者親身體驗角度出發，150-250字，重點說用完的真實感受與改變",
    "從解決生活痛點角度出發，150-250字，先講困擾再帶出商品解方",
    "從限時優惠稀缺感角度出發，150-250字，製造緊迫感促進立即行動",
    "從送禮推薦角度出發，150-250字，適合節慶送禮的理由與產品優點",
    "從CP值比較角度出發，150-250字，說明為何這是市場上最值得買的選擇",
]


def ai_write_copy(brand: str, name: str, desc: str, category: str) -> str:
    """呼叫 Gemini 以隨機角度生成獨特推廣文案，避免每次重複。"""
    if ai_client:
        from google.genai import types
        angle = random.choice(_COPY_ANGLES)
        prompt = f"""你是台灣頂級聯盟行銷文案師。
請為以下品牌撰寫一篇 Facebook／LINE 群組高轉換率推廣貼文。

要求：
1. 繁體中文台灣口語，不要像廣告，要像真人心得
2. 適度使用 Emoji（不要每句都用）
3. 寫作角度：{angle}
4. 結尾必須有明確 CTA（Call to Action）
5. 禁止使用「我要分享」「超值好物」「必買」這類陳腔濫調開頭

品牌：{brand}
活動名稱：{name}
商品特色：{desc}
類別：{category}"""
        try:
            resp = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.92, max_output_tokens=500)
            )
            return resp.text.strip()
        except Exception as e:
            print(f"[AI] ⚠️  Gemini 呼叫失敗: {e}，改用範本")

    # 備用範本（有 API 時不會走到這）
    templates = {
        "購物商城":    f"🛒 【{brand}】近期優惠真的很實在～\n{desc}\n\n手刀點連結查看👇，錯過要等很久！🔥",
        "3C家電":      f"📱 科技控注意！【{brand}】現在正是入手時機！\n{desc}\n\n點連結查看最新優惠👇",
        "美容保養/服飾精品": f"✨ 【{brand}】用過就回不去了～\n{desc}\n\n手刀點連結搶購👇 庫存有限！💄",
        "教育學習":    f"📚 【{brand}】投資自己最划算！\n{desc}\n\n趁特價趕快入手👇 投資自己最實在💡",
        "休閒旅遊":    f"✈️ 【{brand}】旅遊優惠登場！\n{desc}\n\n點連結查看行程👇 訂越早越便宜！🏖️",
        "美食保健":    f"🍽️ 【{brand}】吃過一次就愛上！\n{desc}\n\n點連結搶購👇 值得長期回購！😋",
    }
    return templates.get(category, f"🌟 【{brand}】限時優惠！\n{desc}\n\n點連結馬上查看👇")


def publish_to_webhook(post_text: str, link: str) -> None:
    """推播至 Webhook（未設定則跳過）。"""
    if not WEBHOOK_URL or WEBHOOK_URL.strip() == "":
        return
    try:
        payload = {
            "text": f"{post_text}\n\n👉 立即查看：\n{link}",
            "timestamp": datetime.now().isoformat()
        }
        resp = requests.post(
            WEBHOOK_URL,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if resp.status_code in [200, 204]:
            print("[Webhook] 🎉 推播成功")
        else:
            print(f"[Webhook] ⚠️  狀態碼 {resp.status_code}")
    except Exception as e:
        print(f"[Webhook] ❌ 推播失敗: {e}")


def save_log(records: list) -> None:
    log_path = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"[系統] 📝 推廣紀錄 → {os.path.basename(log_path)}")


def generate_html_page(records: list) -> None:
    """生成 SEO 最佳化靜態 HTML + Sitemap + JSON-LD 結構化資料。"""
    now_str  = datetime.now().strftime("%Y/%m/%d %H:%M")
    iso_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    # ── JSON-LD 結構化資料（讓 Google 更容易收錄）──
    items_ld = []
    for r in records:
        items_ld.append({
            "@type": "ListItem",
            "position": records.index(r) + 1,
            "name": r["brand"],
            "url": r["affiliate_link"]
        })
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "每日精選好物特惠",
        "description": "iChannels 聯盟行銷精選優惠商品，每日自動更新",
        "dateModified": iso_date,
        "itemListElement": items_ld
    }, ensure_ascii=False)

    # ── 商品卡片 HTML ──
    cards_html = ""
    for r in records:
        safe_copy  = r["copy"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        safe_brand = r["brand"].replace("<", "&lt;").replace(">", "&gt;")
        safe_cat   = r["category"].replace("<", "&lt;").replace(">", "&gt;")
        cards_html += f"""
  <article class="card" itemscope itemtype="https://schema.org/Product">
    <div class="badge">{safe_cat}</div>
    <h2 itemprop="name">{safe_brand}</h2>
    <div class="copy" itemprop="description">{safe_copy}</div>
    <a class="btn" href="{r['affiliate_link']}" target="_blank" rel="sponsored noopener">
      👉 立即查看優惠
    </a>
  </article>"""

    # ── 分類導覽 ──
    cats = sorted(set(r["category"] for r in records))
    cat_nav = " | ".join(f'<a href="#{c.replace("/","_")}">{c}</a>' for c in cats)

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="每日精選 iChannels 合作品牌優惠，涵蓋購物商城、3C家電、旅遊、美食，AI每日自動更新最划算好物。">
<meta name="keywords" content="momo優惠,蝦皮折扣,Dyson特賣,Nike官網,Klook優惠,Agoda訂房,博客來折扣,聯盟行銷推薦">
<meta property="og:title" content="每日精選好物特惠 | AI自動更新">
<meta property="og:description" content="精心挑選最划算優惠，每4小時AI自動刷新，錯過可惜！">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://masa032.github.io/ichannels-promo/index.html">
<title>每日精選好物特惠 | AI自動更新優惠情報 {datetime.now().strftime("%Y/%m")}</title>
<script type="application/ld+json">{jsonld}</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Noto Sans TC',system-ui,sans-serif;background:#f4f6fb;color:#333;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
header{{background:linear-gradient(135deg,#c2185b,#f57c00);color:#fff;text-align:center;padding:2.5rem 1rem 1.5rem}}
header h1{{font-size:clamp(1.4rem,4vw,2rem);margin-bottom:.5rem}}
header p{{font-size:.88rem;opacity:.88}}
.updated{{font-size:.78rem;opacity:.7;margin-top:.4rem}}
nav.cats{{background:#fff;border-bottom:1px solid #eee;padding:.6rem 1rem;text-align:center;font-size:.82rem;color:#c2185b;overflow-x:auto;white-space:nowrap}}
nav.cats a{{margin:0 .6rem;color:#c2185b;font-weight:600}}
nav.cats a:hover{{text-decoration:underline}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1.4rem;padding:1.8rem;max-width:1200px;margin:0 auto}}
.card{{background:#fff;border-radius:14px;padding:1.4rem;box-shadow:0 2px 14px rgba(0,0,0,.07);display:flex;flex-direction:column;gap:.75rem;transition:transform .15s,box-shadow .15s}}
.card:hover{{transform:translateY(-3px);box-shadow:0 6px 20px rgba(0,0,0,.12)}}
.badge{{display:inline-block;background:#fce4ec;color:#c2185b;font-size:.72rem;padding:.18rem .65rem;border-radius:99px;font-weight:700;width:fit-content}}
.card h2{{font-size:1rem;color:#1a1a1a;line-height:1.45;font-weight:700}}
.copy{{font-size:.85rem;color:#555;line-height:1.75;flex:1}}
.btn{{display:block;background:linear-gradient(135deg,#c2185b,#f57c00);color:#fff !important;text-align:center;padding:.75rem 1rem;border-radius:9px;font-weight:700;font-size:.9rem;margin-top:auto;transition:opacity .2s;letter-spacing:.03em}}
.btn:hover{{opacity:.87}}
footer{{text-align:center;padding:2rem 1rem;font-size:.78rem;color:#aaa;border-top:1px solid #eee;margin-top:1rem}}
footer a{{color:#c2185b}}
@media(max-width:480px){{.grid{{padding:1rem;gap:1rem}}}}
</style>
</head>
<body>
<header>
  <h1>🛍️ 每日精選好物特惠</h1>
  <p>AI 精選 iChannels 合作品牌，幫你找最值得買的優惠</p>
  <p class="updated">📅 自動更新時間：{now_str}</p>
</header>
<nav class="cats">{cat_nav}</nav>
<main>
  <div class="grid">
{cards_html}
  </div>
</main>
<footer>
  本站使用聯盟行銷連結（Affiliate Links），點擊購買不會增加您任何費用，感謝支持 🙏<br>
  <a href="sitemap.xml">Sitemap</a>
</footer>
</body>
</html>"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[系統] 🌐 SEO HTML 已生成 → output/index.html")

    # ── Sitemap ──────────────────────────────────────────────────────────────
    sitemap_path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://masa032.github.io/ichannels-promo/index.html</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"[系統] 🗺️  Sitemap 已生成 → output/sitemap.xml")

    # ── robots.txt ───────────────────────────────────────────────────────────
    robots_path = os.path.join(OUTPUT_DIR, "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: https://masa032.github.io/ichannels-promo/sitemap.xml\n")
    print(f"[系統] 🤖 robots.txt 已生成 → output/robots.txt")


# ── 主流程 ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(f"🚀 iChannels 全自動推廣引擎 v3.0 啟動")
    print(f"   帳號: masatsai032@gmail.com")
    print(f"   聯盟ID: {ICHANNELS_AFFILIATE_ID}")
    print(f"   時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    campaigns = load_campaigns()
    print(f"[系統] 📋 載入 {len(campaigns)} 個推廣任務\n")

    records = []
    for c in campaigns:
        print(f"── 處理: {c['brand']} ({c['id']}) ──")

        copy = ai_write_copy(c["brand"], c["name"], c["desc"], c["category"])
        link = make_affiliate_link(c["url"], c["uid"])

        print(f"[文案] {copy[:60]}...")
        print(f"[連結] {link[:80]}...")

        publish_to_webhook(copy, link)

        records.append({
            "id":            c["id"],
            "brand":         c["brand"],
            "category":      c["category"],
            "copy":          copy,
            "affiliate_link": link,
            "timestamp":     datetime.now().isoformat()
        })
        print()

    # 生成 HTML + 儲存日誌
    generate_html_page(records)
    save_log(records)

    print("=" * 60)
    print(f"✅ 全部完成！共處理 {len(records)} 個品牌")
    print(f"   📄 推廣頁: output/index.html")
    print(f"   📝 日誌:   logs/")
    print("=" * 60)


if __name__ == "__main__":
    main()
