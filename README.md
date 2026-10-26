# 台美股波段漲跌天數與累積漲跌幅試算分析工具
# Taiwan & US Stock Duration & Percentage Analyzer
### 整合大盤加權指數 (TAIEX)、扣除五大權值股動態分析、美股四大指數 (標普 500 / 費城半導體 SOX / 那斯達克 / 道瓊)、美股與全球 ETF (VT/VTI/BND/TSM/NVDA/GOOGL)、GitHub Pages 部署與 Actions 自動更新排程

[![Generative UI Compliant](https://img.shields.io/badge/Generative_UI-Compliant-success?style=flat-square)](https://github.com)
[![Offline Ready](https://img.shields.io/badge/Dependencies-Zero_Standalone-blue?style=flat-square)](https://github.com)
[![Bilingual Parity](https://img.shields.io/badge/i18n-繁體中文%20%7C%20English-purple?style=flat-square)](https://github.com)
[![Dual Theme](https://img.shields.io/badge/Theme-Dark%20%26%20Light-orange?style=flat-square)](https://github.com)
[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub_Pages-blue?style=flat-square&logo=github)](https://pages.github.com/)
[![Auto Updater](https://img.shields.io/badge/GitHub_Actions-Auto_Update_Daily-green?style=flat-square&logo=githubactions)](https://github.com/features/actions)

本工具為依據 **Generative UI & Production WebApp 規範** 打造的單檔案、零外部相依、離線可執行的互動式網頁應用程式。同時涵蓋 **台股五大權值股**（台積電 2330、聯發科 2454、鴻海 2317、廣達 2382、台達電 2308）、**臺灣加權指數（大盤 TAIEX）與「扣除五大權值股後之大盤變化（TAIEX Ex-Big 5）」**，以及 **6 檔美股與全球核心 ETF（VT、VTI、BND、TSM 台積電 ADR、NVDA 輝達、GOOGL Google）**，並附帶 **GitHub Actions 每日定時盤後自動更新與 GitHub Pages 一鍵發佈工作流**！

---

## 📑 目錄 / Table of Contents

- [1. 快速開始：部署至 GitHub Pages 與自動更新 / GitHub Pages & Auto-Update Guide](#1-快速開始部署至-github-pages-與自動更新--github-pages--auto-update-guide)
- [2. 技術架構與開發回饋 / Architecture & Technical Feedback](#2-技術架構與開發回饋--architecture--technical-feedback)
- [3. 大盤與扣除五大權值結構拆解 / Market & Ex-Big 5 Decomposition](#3-大盤與扣除五大權值結構拆解--market--ex-big-5-decomposition)
- [4. 支援標的與大盤權重 / Supported Symbols & Market Weights](#4-支援標的與大盤權重--supported-symbols--market-weights)
- [5. 統計指標與計算公式 / Metrics & Formulas](#5-統計指標與計算公式--metrics--formulas)
- [6. Generative UI 規範實踐 / Generative UI Protocol Compliance](#6-generative-ui-規範實踐--generative-ui-protocol-compliance)
- [7. 檔案結構與元件清單 / File Structure & Manifest](#7-檔案結構與元件清單--file-structure--manifest)

---

## 1. 快速開始：部署至 GitHub Pages 與自動更新 / GitHub Pages & Auto-Update Guide

透過 **GitHub Pages (免費靜態託管)** 搭配 **GitHub Actions (免費定時自動排程)**，您無須購買伺服器或負擔任何費用，即可建立全自動每日盤後更新的台股分析網站！

```
                      [GitHub Actions 定時工作流]
                    每個交易日下午 14:00 (UTC 06:00)
                                 │
                                 ▼ (無 CORS 限制, 執行 update_prices.py)
                   從 Yahoo / TWSE 抓取最新收盤序列
                                 │
                                 ▼
                     自動更新 latest_market_data.json
                                 │
                                 ▼ (git commit & push)
                  推送至 GitHub 專案存儲庫 (Repository)
                                 │
                                 ▼
              [GitHub Pages 自動重新發佈靜態站點]
                                 │
                                 ▼ (同源 HTTPS 讀取，零 CORS 錯誤)
           使用者開啟網頁即刻取得最新行情，完全自動化！
```

---

### 步驟 1：將專案推送到 GitHub (Push to GitHub)

在專案目錄下開啟終端機（PowerShell 或 Bash）：
```bash
git init
git add .
git commit -m "feat: initial commit with TAIEX analyzer & auto-updater"
git branch -M main
git remote add origin https://github.com/<您的GitHub帳號>/<您的專案名稱>.git
git push -u origin main
```

---

### 步驟 2：啟用 GitHub Pages (Enable GitHub Pages)

1. 前往您的 GitHub 專案頁面，點選頂部 **Settings**（設定）。
2. 在左側選單點選 **Pages**。
3. 在 **Build and deployment** 區塊：
   - **Source** 選擇 `Deploy from a branch`。
   - **Branch** 選擇 `main`，資料夾選擇 `/ (root)`。
   - 點擊 **Save**。
4. 約等待 1 分鐘，頂部將顯示您的專屬網站網址：  
   `https://<您的GitHub帳號>.github.io/<您的專案名稱>/`

---

### 步驟 3：開啟 GitHub Actions 寫入權限 (Enable Workflow Permissions)

為了讓定時更新機器人可以把最新的股價資料寫入存儲庫：
1. 進入 GitHub 專案頁面，點選 **Settings** -> 左側 **Actions** -> **General**。
2. 滾動至底部 **Workflow permissions**：
   - 勾選 **「Read and write permissions」**（讀寫權限）。
   - 點擊 **Save**。

---

### 步驟 4：自動定時更新與手動觸發 (Daily Automation & Manual Run)

本專案已預先建置 [`.github/workflows/update_prices.yml`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/stock%20inculde%20big%205/.github/workflows/update_prices.yml)：
- **自動執行時間**：每週一至週五台灣時間 **14:00**（台股 13:30 收盤後半小時，即 UTC 06:00），自動執行更新並發佈。
- **隨時手動立即更新**：
  1. 進入專案頁面點選頂部 **Actions** 標籤。
  2. 左側選取 **Daily Taiwan Stock Price Auto-Update**。
  3. 點選右側 **Run workflow** -> 點擊綠色 **Run workflow** 按鈕。
  4. 約 30 秒內即可抓取完成並同步發布至 GitHub Pages！

---

## 2. 技術架構與開發回饋 / Architecture & Technical Feedback

### Q1：股票價格從哪裡來？(Where do stock prices come from?)
1. **臺灣證券交易所官方開放資料 (TWSE OpenAPI)**：
   - 端點：`https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL`
   - 特點：涵蓋台灣全部上市股票收盤行情，官方權威來源，免 API Key。
2. **Yahoo Finance API**：
   - 端點：`https://query1.finance.yahoo.com/v8/finance/chart/{代碼}.TW?interval=1d&range=1y`
   - 特點：支援長達數年之每日除權息調整收盤價（Adjusted Close）、加權大盤指數（`^TWII`），反應迅速。
3. **本土開發者 API (FinMind / 富果 Fugle)**：
   - 適合盤中秒級即時五檔報價與籌碼串接。

---

### Q2：網頁能不能「自己直接更新」？為什麼需要中介腳本？(Why CORS prevents direct in-browser fetch?)
- **瀏覽器的跨來源安全政策 (Cross-Origin Resource Sharing, CORS)**：
  - 當靜態網頁直接在瀏覽器執行時，如果以 JavaScript `fetch()` 呼叫 TWSE 或 Yahoo Finance，瀏覽器會因為官方伺服器**沒有返回 `Access-Control-Allow-Origin: *` 標頭**而強制阻斷連線。
- **我們的最佳解法 (The Serverless Solution)**：
  - **Python 腳本 (`update_prices.py`)**：不受瀏覽器 CORS 限制，3 秒內完成連線抓取，輸出同源的 `latest_market_data.json`。
  - **GitHub Pages 同源機制**：當部署至 GitHub Pages 後，`index.html` 與 `latest_market_data.json` 位於**同一個網域名稱下 (Same-Origin)**，`fetch("latest_market_data.json?_t=" + Date.now())` 享有 100% 暢通連線，完全不受 CORS 阻擋！
  - **離線韌性機制**：即便在完全沒有網路的極端離線環境，`index.html` 內嵌的歷史樣本保證網頁依然能正常運算各項波段指標與圖表。

---

## 3. 大盤與扣除五大權值結構拆解 / Market & Ex-Big 5 Decomposition

在台灣股市中，前五大權值股對加權指數具備極大主導力：

```
全市場加權大盤 (TAIEX, 100%)
  │
  ├── 🏢 五大權值股 (合計權重 45.0%)
  │     ├── 台積電 (2330.TW)  34.5%  ── 晶圓代工龍頭 (一人武林)
  │     ├── 聯發科 (2454.TW)   3.5%  ── IC設計旗艦
  │     ├── 鴻海   (2317.TW)   4.2%  ── 電子代工與AI伺服器
  │     ├── 廣達   (2382.TW)   1.5%  ── 雲端運算與AI伺服器
  │     └── 台達電 (2308.TW)   1.3%  ── 智慧電源管理
  │
  └── 🔍 扣除五大後其餘市場 (TAIEX Ex-Big 5, 合計權重 55.0%)
        └── 全市場其餘千檔上市櫃個股 (真實反映中小型與非權值股的市場體感)
```

本工具在專屬的 **「大盤指數與扣除五大權值股動態結構分析儀表板」** 中，為您提供：
1. **加權指數 (大盤 TAIEX)**：總點數變化、總報酬率、上漲天數、勝率與連續波段紀錄。
2. **五大權值股合計貢獻**：合計權重（45.0%）、貢獻大盤點數與在大盤總漲點中所佔比例（%）。
3. **扣除五大後大盤真實表現**：非五大權值股之累積漲跌百分比、其餘股票真實勝率、連漲與連跌波段。
4. **市場廣度與拉積盤診斷**：自動過濾出「大盤漲但個股跌」的拉積失真日數與「全面普漲良性日數」。

---

## 4. 支援標的與大盤權重 / Supported Symbols & Market Weights

### 🇹🇼 台股與大盤指數 (Taiwan Stocks & Benchmarks)
| 標的代號 | 市場/幣別 | 中文名稱 | 英文名稱 | 大盤權重 | 代表色 | 預設狀態 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TAIEX** | TW (Pts) | **加權指數 (大盤)** | **TAIEX Index** | **100.0%** | `#f43f5e` | 基準指標 |
| **EX_BIG5** | TW (Pts) | **扣除五大後大盤** | **TAIEX Ex-Big 5** | **55.0%** | `#06b6d4` | 基準指標 |
| **2330** | TW (TWD) | **台積電** | **TSMC** | **34.5%** | `#ef4444` | **預設啟用** |
| **2454** | TW (TWD) | **聯發科** | **MediaTek** | **3.5%** | `#38bdf8` | **預設啟用** |
| **2317** | TW (TWD) | **鴻海** | **Foxconn** | **4.2%** | `#a855f7` | 可選標的 |
| **2382** | TW (TWD) | **廣達** | **Quanta** | **1.5%** | `#f59e0b` | 可選標的 |
| **2308** | TW (TWD) | **台達電** | **Delta** | **1.3%** | `#10b981` | 可選標的 |

### 📈 美股四大核心指數 (US Major Market Indices)
| 標的代號 | Yahoo 代號 | 市場/單位 | 中文名稱 | 英文名稱 | 類別說明 | 代表色 | 預設狀態 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SP500** | `^GSPC` | US (Pts) | **標普 500 指數** | **S&P 500 Index** | 美國 500 大上市企業市值加權基準指數 | `#f97316` | **預設啟用** |
| **SOX** | `^SOX` | US (Pts) | **費城半導體指數** | **PHLX Semiconductor (SOX)** | 全球半導體設計、設備與晶圓製造核心指標 | `#ec4899` | **預設啟用** |
| **NASDAQ** | `^IXIC` | US (Pts) | **那斯達克指數** | **Nasdaq Composite** | 美國科技與高成長創新企業代表指數 | `#8b5cf6` | **預設啟用** |
| **DJI** | `^DJI` | US (Pts) | **道瓊工業指數** | **Dow Jones Industrial** | 美國 30 大藍籌工業、金融與消費巨頭指數 | `#3b82f6` | 可選標的 |

### 🇺🇸 美股與全球 ETF (US Stocks & Global ETFs)
| 標的代號 | 市場/幣別 | 中文名稱 | 英文名稱 | 類別說明 | 代表色 | 預設狀態 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VT** | US (USD) | **VT (全球股票ETF)** | **Vanguard Total World ETF** | 全球股票指數 ETF | `#0ea5e9` | **預設啟用** |
| **VTI** | US (USD) | **VTI (全美股票ETF)** | **Vanguard Total Stock Market ETF** | 整體美國股市 ETF | `#6366f1` | **預設啟用** |
| **BND** | US (USD) | **BND (總體債券ETF)** | **Vanguard Total Bond Market ETF** | 美國投資級總體債券 ETF | `#14b8a6` | **預設啟用** |
| **TSM** | US (USD) | **台積電 ADR** | **TSMC ADR** | 晶圓代工龍頭美國存託憑證 | `#fb7185` | **預設啟用** |
| **NVDA** | US (USD) | **輝達 (NVIDIA)** | **NVIDIA** | AI 算力與 GPU 加速運算霸主 | `#84cc16` | **預設啟用** |
| **GOOGL** | US (USD) | **Google (Alphabet)** | **Google (Alphabet)** | 雲端、搜尋與 Gemini AI 巨頭 | `#eab308` | **預設啟用** |

### 🌐 總經景氣指標分頁：CPI 與 PMI 專頁 (Macro CPI & PMI Index Tab)
頁面頂部內建雙分頁切換器（`台美股波段與大盤結構分析` ⇄ `總經景氣指標：CPI 與 PMI 專頁`），支援 6 項核心美台總經指標、24 個月趨勢圖（配備頂部中文圖例列、右側防重疊引線標籤、高對比月份軸與滑鼠懸停十字線提示框）、景氣四象限配置時鐘與 CSV 匯出：

| 指標代號 | 區域/類別 | 中文名稱 | 英文名稱 | 關鍵榮枯/目標基準線 | 代表色 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **US_CPI** | US · CPI (%) | **美國 CPI 年增率** | **US Headline CPI YoY** | **2.0% (Fed 目標線)** | `#ef4444` |
| **US_CORE_CPI** | US · CPI (%) | **美國核心 CPI 年增率** | **US Core CPI YoY** | **2.0% (Fed 核心目標)** | `#f97316` |
| **TW_CPI** | TW · CPI (%) | **台灣 CPI 年增率** | **TW Headline CPI YoY** | **2.0% (央行通膨警戒線)** | `#eab308` |
| **US_ISM_PMI** | US · PMI (Index) | **美國 ISM 製造業 PMI** | **US ISM Manufacturing PMI** | **50.0 (景氣榮枯分水嶺)** | `#38bdf8` |
| **US_ISM_NMI** | US · PMI (Index) | **美國 ISM 服務業 PMI** | **US ISM Services PMI** | **50.0 (景氣榮枯分水嶺)** | `#6366f1` |
| **TW_PMI** | TW · PMI (Index) | **台灣製造業 PMI (CIER)** | **TW Manufacturing PMI** | **50.0 (景氣榮枯分水嶺)** | `#10b981` |

---

### 💡 CPI 與 PMI 判讀指南：到底「愈高愈好」還是「愈低愈好」？(How to Read CPI & PMI)

#### 1. 🔥 CPI 消費者物價指數年增率 (通膨率 YoY %)
> **核心結論：❌ 不是愈高愈好，也不是愈低愈好 ➡️ 「維持在 `1.5% ~ 2.5%`（貼近 `2.0%` 央行目標線）最理想！」**

| 水位區間 | 景氣與物價意義 | 對台美股市 (`2330`/`NVDA`/`VT`) 與債券 (`BND`) 之影響 |
| :--- | :--- | :--- |
| **🟢 `1.5% ~ 2.5%`**<br>*(溫和舒適區 · 最佳)* | **金髮女孩經濟 (Goldilocks)**：需求健康、物價穩定，企業具備合理定價與獲利成長空間。 | **股債雙漲最有利環境**：聯準會 (Fed) 與台灣央行無須升息、甚至可降息寬鬆，最有利台積電 (`2330`)、輝達 (`NVDA`)、全市場股票 ETF (`VT`/`VTI`) 與總體債券 ETF (`BND`) 同步上漲。 |
| **🔴 `> 3.0%`**<br>*(通膨過熱區 · 愈高愈危險)* | **通膨失控升溫**：生活與生產成本飆升、侵蝕實質購買力。 | **股債雙殺風險**：迫使央行**升息或長期維持高利率**抽走市場資金，高估值科技股本益比下修，且債券 (`BND`) 因殖利率攀升而下跌。 |
| **🔵 `< 1.0%` 或負值**<br>*(通縮衰退區 · 過低也不好)* | **通縮螺旋警訊 (Deflation)**：內需消費急凍、百業蕭條、企業削價競爭。 | **股市承壓、公債避險**：企業營收與獲利衰退壓抑股市，但央行往往大幅降息救市，推升投資級債券 (`BND`)。 |

#### 2. 🏭 PMI 採購經理人指數 (景氣榮枯 Index)
> **核心結論：⭕ 站上 `50.0` 榮枯分水嶺以上，「在 `51 ~ 58` 擴張區間愈高愈穩健愈好！」（但超過 `60` 需防過熱見頂）**

| 水位區間 | 景氣與訂單意義 | 對台美股市 (`2330`/`2454`/`NVDA`) 之影響 |
| :--- | :--- | :--- |
| **🟢 `50.0 ~ 58.0`**<br>*(景氣擴張區 · 愈高愈好)* | **`50.0` 為榮枯分水嶺**：`> 50` 代表新訂單增加、客戶拉貨積極、工廠擴產、僱用增加。 | **基本面多頭主升段**：直接帶動台股五大權值股（台積電 `2330`、聯發科 `2454`、鴻海 `2317`、廣達 `2382`、台達電 `2308`）與美股 AI 科技巨頭營收與 EPS 持續成長。 |
| **🟡 `> 60.0`**<br>*(極度過熱區 · 居高思危)* | **產能極度緊繃**：供應鏈缺料、交期拉長、原物料搶貨漲價。 | **短多長空警戒**：雖當下財報極佳，但往往伴隨通膨反彈與央行緊縮預期，需留意景氣循環高點反轉。 |
| **🔴 `< 50.0`**<br>*(景氣緊縮區 · 谷底翻揚是買點)* | **景氣收縮與去庫存**：`< 50` 代表訂單萎縮、工廠減產、客戶消化庫存。 | **左側長線佈局法則**：當 PMI 跌落至 `43 ~ 46` 谷底區並開始**連續回升（連升轉折）**時，往往對應股市庫存調整結束、迎來波段報酬率最高的長線買點！ |

---

### 🧭 CPI × PMI 景氣四象限時鐘 (4-Quadrant Macro Regime Clock)

```
                         ▲ CPI 通膨年增率 (Inflation)
                         │
   【象限 III：停滯性通膨警戒】          │          【象限 II：過熱與再通膨】
    PMI < 50 (收縮) + CPI 偏高           │           PMI > 50 (擴張) + CPI 升溫
    ⚠️ 央行難降息，宜提高防禦、嚴控回撤   │           🔥 具定價權龍頭股撐盤，債券 BND 承壓
 ────────────────────────┼───────────────┼───────────────────────► PMI 景氣榮枯 (50.0)
   【象限 IV：景氣放緩 / 降息週期】       │          【象限 I：金髮女孩軟著陸 (最佳)】
    PMI < 50 (收縮) + CPI 回落           │           PMI > 50 (擴張) + CPI 溫和 (≈2%)
    🛡️ 債券 BND 領漲，股市待谷底分批佈局  │           🌟 台股五大權值與美股科技、股債齊漲！
                         │
```

---

### 🔄 CPI 與 PMI 會自動更新嗎？更新機制與每月公佈時程註解 (Auto-Update & Release Schedule)

1. **為什麼股價每天跳動，而 CPI / PMI 是一個月更新一次？**
   - **台美股價（分頁 1）**：屬於**每日交易行情**，每個交易日收盤後變動（由 GitHub Actions 每週一至週五 14:00 自動執行 `update_prices.py` 抓取 Yahoo Finance / TWSE）。
   - **CPI 與 PMI（分頁 2）**：屬於**官方「月度總經統計指標」（每月僅公佈 1 次，非每日變動）**，在下次官方公佈日前數值保持固定。

2. **自動更新串接機制 (`update_prices.py` + `latest_market_data.json`)**：
   - `update_prices.py` 已內建 `fetch_bls_cpi_yoy()` 函式，直接連線 **美國勞工統計局 (U.S. Bureau of Labor Statistics, BLS) 官方免金鑰公開 API (`https://api.bls.gov/publicAPI/v1/timeseries/data/`)**：
     - 自動抓取 `CUUR0000SA0`（美國整體 CPI 指數）與 `CUUR0000SA0L1E`（美國核心 CPI 指數）。
     - 自動比對去年同月指數，計算最新 **YoY 年增率 (%)** 並寫入 `latest_market_data.json` 的 `__MACRO_DATA__` 區塊。
   - 當網頁開啟時，`index.html` 的 `ingestExternalDataset()` 會自動讀取 `latest_market_data.json` 內的 `__MACRO_DATA__`，將最新月份的 CPI 與 PMI 數據同步渲染至圖表與表格中。

3. **美台各項指標官方固定公佈時程表（台灣時間）**：

| 總經指標 | 發佈機構 | 每月固定公佈時間 | 自動同步/更新方式 |
| :--- | :--- | :--- | :--- |
| **🇺🇸 美國 ISM 製造業 PMI** | 美國供應管理協會 (ISM) | 每月 **第 1 個營業日** 22:00 / 23:00 | 隨 `latest_market_data.json` (`__MACRO_DATA__`) 同步 |
| **🇺🇸 美國 ISM 服務業 PMI** | 美國供應管理協會 (ISM) | 每月 **第 3 個營業日** 22:00 / 23:00 | 隨 `latest_market_data.json` (`__MACRO_DATA__`) 同步 |
| **🇹🇼 台灣製造業 PMI** | 中華經濟研究院 (CIER) | 每月 **月初（約 1～3 日）** 14:00 | 隨 `latest_market_data.json` (`__MACRO_DATA__`) 同步 |
| **🇹🇼 台灣 CPI 年增率** | 行政院主計總處 (DGBAS) | 每月 **上旬（約 5～8 日）** 16:00 | 隨 `latest_market_data.json` (`__MACRO_DATA__`) 同步 |
| **🇺🇸 美國 CPI / 核心 CPI** | 美國勞工統計局 (BLS) | 每月 **中旬（約 10～15 日）** 20:30 / 21:30 | **`update_prices.py` 連線官方 BLS API 自動換算更新** |

---

## 5. 統計指標與計算公式 / Metrics & Formulas

1. **五大權值股合計貢獻大盤點數**:
   $$\Delta \text{Pts}_{\text{Big5}} = \sum_{t=1}^T \left( P_{\text{TAIEX}, t-1} \times \sum_{i \in \text{Big5}} w_i R_{i, t} \right)$$

2. **扣除五大權值後日報酬率 (Ex-Big 5 Daily Return)**:
   $$R_{\text{Ex-Big5}, t} = \frac{R_{\text{TAIEX}, t} - \sum_{i \in \text{Big5}} w_i R_{i, t}}{0.550}$$

3. **扣除五大權值後累積報酬率 (Ex-Big 5 Total Return)**:
   $$\text{Return}_{\text{Ex-Big5}} = \left[ \prod_{t=1}^T (1 + R_{\text{Ex-Big5}, t}) - 1 \right] \times 100\%$$

4. **拉積失真日數 (Divergence Day)**:
   $$\text{Divergence Day}: \quad R_{\text{TAIEX}, t} > 0 \quad \text{且} \quad R_{\text{Ex-Big5}, t} < 0$$

5. **全面普漲日數 (Broad Rally Day)**:
   $$\text{Broad Rally Day}: \quad R_{\text{TAIEX}, t} > 0 \quad \text{且} \quad R_{\text{Ex-Big5}, t} > 0$$

6. **期間最大回撤 (Maximum Drawdown, MDD)**:
   $$\text{MDD} = \max_{t \in [0, T]} \left( \frac{\max_{s \in [0, t]} P_s - P_t}{\max_{s \in [0, t]} P_s} \right) \times 100\%$$

---

## 6. Generative UI 規範實踐 / Generative UI Protocol Compliance

- **雙主題支援 (Dark & Light Mode)**：頂部 `☀️ / 🌙` 切換，支援 WCAG AA 高對比度標準。
- **雙語零外洩對稱原則 (Bilingual Parity)**：頂部 `🌐 切換語言`，全介面標籤對稱封裝，通過 Python 遍歷審計 **0 leaks**。
- **單檔案零依賴保證 (Zero External Dependencies)**：無外部圖表套件 CDN，完全離線運算，在無網路環境下亦能秒級啟動。

---

## 7. 檔案結構與元件清單 / File Structure & Manifest

```
stock inculde big 5/
├── .github/
│   └── workflows/
│       └── update_prices.yml # GitHub Actions 每日盤後定時自動抓取工作流
├── index.html                # 核心互動式單檔案網頁應用程式 (約 118KB)
├── update_prices.py          # 零依賴 Python 自動行情更新器 (約 4KB)
├── latest_market_data.json   # 最新市場行情快照序列檔 (約 220KB)
├── verify_html.py            # 自動化結構與雙語審計腳本
└── README.md                 # 專案完整記錄與部署說明檔 (本檔案)
```

---

*紀錄日期：2026-10-24*  
*開發依據：Antigravity Generative UI Engineering Standard*
