# 🚀 iChannels 通路王 全自動 AI 推廣引擎 v2.0

> 使用 Gemini AI 自動撰寫文案 + 自動生成分潤連結 + Webhook 自動發布

---

## 📁 檔案結構

```
【通路王】全自動代理聯盟行銷/
├── ichannels_auto_promo.py   ← 主程式
├── .env.example              ← 設定檔範本 (複製成 .env 再填寫)
├── .env                      ← 您的實際設定 (自行建立，勿上傳)
├── requirements.txt          ← 套件需求
├── README.md                 ← 本說明檔
└── logs/                     ← 推廣紀錄 (自動建立)
    └── log_YYYYMMDD.json
```

---

## ⚡ 快速開始

### 步驟 1：安裝套件

```powershell
cd "C:\Users\A.T\Documents\AI_Automatic\【通路王】全自動代理聯盟行銷"
pip install -r requirements.txt
```

### 步驟 2：建立 .env 設定檔

```powershell
Copy-Item .env.example .env
notepad .env
```

填入以下資訊：

| 變數名稱 | 說明 | 取得方式 |
|---|---|---|
| `GEMINI_API_KEY` | Gemini API 金鑰 | [Google AI Studio](https://aistudio.google.com) 免費申請 |
| `ICHANNELS_AFFILIATE_ID` | 您的通路王 ID | 已預設為 `af000094185` |
| `WEBHOOK_URL` | 自動發布網址 | Make.com 或 Discord Webhook |

### 步驟 3：執行

```powershell
python ichannels_auto_promo.py
```

---

## 🔗 iChannels 分潤連結說明

根據 iChannels 官方說明，正確的分潤連結格式為：

```
原始商品網址 + ?ic=af000094185&uid=來源標籤
```

範例：
```
https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=1234567&ic=af000094185&uid=site-001
```

`uid` 可自訂來源標籤（如 `line-001`, `fb-001`）方便追蹤哪個管道最有效。

---

## 📡 Webhook 設定 (Make.com 教學)

1. 進入 [Make.com](https://make.com) → 建立新 Scenario
2. 起點選 **Webhooks** → **Custom Webhook** → 建立並複製網址
3. 後續可串接 Facebook Pages / LINE Notify / Discord 等發布節點
4. 將複製的網址填入 `.env` 的 `WEBHOOK_URL`

---

## ⚠️ 注意事項

- `.env` 檔案含 API Key，**絕對不要上傳到 GitHub**
- iChannels 分潤以「成交」計算，非點擊，請重視內容品質
- 請遵守 iChannels 及各平台的推廣規範，勿大量濫發

---

## 📝 更新紀錄

| 版本 | 說明 |
|---|---|
| v2.0 | 修正分潤連結格式、改用安全 .env 設定、升級 Gemini SDK、新增批次處理與日誌功能 |
| v1.0 | 初始版本 |
