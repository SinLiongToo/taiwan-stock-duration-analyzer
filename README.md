# 台美股波段漲跌天數與累積漲跌幅試算分析工具
# Taiwan & US Stock Duration & Percentage Analyzer
### 整合大盤加權指數 (TAIEX)、扣除五大權值股動態分析、美股與全球 ETF (VT/VTI/BND/TSM/NVDA/GOOGL)、GitHub Pages 部署與 Actions 自動更新排程

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

### 🇺🇸 美股與全球 ETF (US Stocks & Global ETFs)
| 標的代號 | 市場/幣別 | 中文名稱 | 英文名稱 | 類別說明 | 代表色 | 預設狀態 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VT** | US (USD) | **VT (全球股票ETF)** | **Vanguard Total World ETF** | 全球股票指數 ETF | `#0ea5e9` | **預設啟用** |
| **VTI** | US (USD) | **VTI (全美股票ETF)** | **Vanguard Total Stock Market ETF** | 整體美國股市 ETF | `#6366f1` | **預設啟用** |
| **BND** | US (USD) | **BND (總體債券ETF)** | **Vanguard Total Bond Market ETF** | 美國投資級總體債券 ETF | `#14b8a6` | **預設啟用** |
| **TSM** | US (USD) | **台積電 ADR** | **TSMC ADR** | 晶圓代工龍頭美國存託憑證 | `#fb7185` | **預設啟用** |
| **NVDA** | US (USD) | **輝達 (NVIDIA)** | **NVIDIA** | AI 算力與 GPU 加速運算霸主 | `#84cc16` | **預設啟用** |
| **GOOGL** | US (USD) | **Google (Alphabet)** | **Google (Alphabet)** | 雲端、搜尋與 Gemini AI 巨頭 | `#eab308` | **預設啟用** |

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
