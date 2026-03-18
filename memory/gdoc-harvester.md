# gdoc-harvester — Web Harvester 收割工具經驗

- Scope: global
- Confidence: [觀]
- Trigger: harvester, Google Docs, Sheets, 收割, Playwright, cookie, export
- Last-used: 2026-03-17
- Confirmations: 11

## Web Harvester

**位置**: `~/.claude/tools/gdoc-harvester/`（技能本體，可上 GIT）
**Skill**: `/harvest`（`~/.claude/commands/harvest.md`）
**Runtime**: 使用者指定工作目錄（預設 `c:/tmp/harvester/`，含 browser-data + output，不進 GIT）

### 踩坑記錄

1. **Playwright Chromium 無法登入 Google** — Google 偵測自動化瀏覽器
   - 解法: `channel="chrome"` + `--disable-blink-features=AutomationControlled`

2. **Chrome profile lock 衝突** — 不能同時用同一個 profile
   - 解法: 複製 Chrome Default 的 Cookies 等關鍵檔到獨立目錄（需先關 Chrome）

3. **`context.request.get()` 不帶 browser cookies** — Playwright 設計限制

4. **`page.evaluate` + `fetch()` 被 CORS 擋** — Google export redirect 跨域

5. **framenavigated race condition** — 同一 doc_id 多次觸發
   - 解法: `on_page_navigate` 在第一個 await 前 `visited.add(url_key)` 佔位

7. **capture_doc/sheet 自殺 bug** — on_page_navigate 已加 visited，capture 又 `if in visited: return`
   - 解法: 移除 capture 的 early return，只保留冪等 `visited.add()`

8. **標題抓取失敗** — Google export HTML 的 `<title>` 常空或只有 doc_id
   - 解法: 多層 fallback: `<title>` → h1/h2/h3 → 第一段文字 → doc_id

9. **Sheets export 全部 401/400** — `context.request.get()` 和 `page.goto(export_url)` 都回傳 400
   - 原因: Google Sheets export redirect 到 `googleusercontent.com`，需要正確 Referer + session context
   - 解法: `sheet_download()` — 先開 Sheet 編輯頁建立 context，再 `page.evaluate('window.location.href=...')` 觸發
   - 端點: 優先 `gviz/tq?tqx=out:csv` → fallback `/export?format=csv`

10. **GitLab 登入無法持續** — 放棄複製 cookies，改為首次在收割瀏覽器手動登入，persistent context 記住

11. **Google export URL 觸發下載而非頁面載入**
    - 解法: `context.request.get()` 優先 + `asyncio.wait` race fallback

12. **Google 權限不足錯誤頁偵測**
    - 解法: 檢查 `page.content()` 含「無法開啟」「很抱歉」→ 回傳 403

13. **GitLab/GitHub SPA 頁面不觸發 framenavigated** — SPA 用 pushState 導航
    - 原因: `framenavigated` 只偵測完整頁面載入，SPA 的 `history.pushState` 不觸發
    - 解法: **SPA URL poller** — 每 2 秒掃描所有分頁 `page.url`，偵測變化後觸發 `on_page_navigate()`
    - 與 `framenavigated` 並存，不衝突

14. **知乎/YouTube 等 JS-rendered 頁面內容太少** — Playwright 拿到的 HTML 缺乏主要內容
    - 現狀: 跳過（< 50 chars），未來可考慮 `page.wait_for_selector()` 等待渲染

### 架構

```
classify_url(url) → (key, type) | None
  ├─ Google Docs/Sheets/Slides → 專用 export 邏輯
  ├─ GitLab (hostname 含 "gitlab" 或 /-/ 路徑) → capture_page + try_raw_content
  ├─ GitHub (github.com) → capture_page + try_raw_content
  ├─ SKIP_URL_PATTERNS 命中 → None（不收割）
  └─ 其他 → capture_page（通用 HTML→Markdown）
```

- **偵測引擎**: `framenavigated`（完整導航）+ SPA URL poller（pushState）
- **Google 專用**: `page_fetch()` / `sheet_download()` / `capture_slide()`
- **通用擷取**: `capture_page()` — 平台 CSS selector (`CONTENT_SELECTORS`) + noise 移除 + `markdownify`
- **Raw content**: `try_raw_content()` — GitLab wiki `.md` / blob `/-/raw/`、GitHub `raw.githubusercontent.com`
- **Dashboard**: `http://127.0.0.1:8787` — 即時進度（Docs/Sheets/Slides/Pages 統計 + type badge）
- **結束**: 關閉瀏覽器 → `_INDEX.md` 總清單

### 安全設計

- 技能本體零硬編碼路徑、零公司 URL
- browser-data（含所有網站 cookies）存在 runtime 工作目錄，不進 git
- Skill 流程提醒使用者事後清理敏感資料

**Why:** 使用者要把散落在 Google Drive / GitLab / 各處的公司文件整理收割
**How to apply:** `/harvest` skill 使用或後續改進時參考
