# Node.js / TypeScript 生態系知識庫

- Scope: global
- Confidence: [固]
- Trigger: Node.js, NodeJS, npm, npx, package.json, node_modules, TypeScript, tsc, pm2, ecosystem.config, JavaScript, JS, TS, ESM, CommonJS, CJS
- Last-used: 2026-04-09
- Confirmations: 137
- Related: toolchain, fail-env

## 知識

### npm vs npx

- [固] **npm** = Node Package Manager，套件管理員。負責安裝（`npm install`）、管理依賴（`package.json` + `node_modules/`）
- [固] **npx** = Node Package Execute，套件執行器。隨 npm 5.2+ 內建
- [固] `npx <cmd>` 從 `node_modules/.bin/` 找到本地安裝的指令並執行，不需全域安裝
- [固] 三種等效寫法：
  - `npx pm2 start ...`（最常用）
  - `./node_modules/.bin/pm2 start ...`（完整路徑）
  - 在 package.json scripts 裡直接寫 `pm2 start ...`（scripts 自動加 node_modules/.bin 到 PATH）

### 全域安裝 vs 本地安裝

- [固] `npm install -g pm2` → 裝到系統 PATH（如 `/usr/local/bin/pm2`），可直接呼叫 `pm2`
- [固] `npm install pm2` → 裝到專案 `node_modules/`，需透過 `npx pm2` 呼叫
- [固] 網路教學多用全域安裝風格（`pm2 start`），catclaw 用本地安裝（`npx pm2`）確保版本鎖定、clone 即可用
- [固] 本地安裝好處：版本跟 package-lock.json 鎖定、不依賴環境、換機器零設定

### PM2 程序管理

- [固] PM2 = Node.js 的 process manager，用於背景常駐、crash 自動重啟、log 管理
- [固] `ecosystem.config.cjs` 是 PM2 設定檔，定義 script 路徑、watch 目錄、環境變數
- [固] watch 機制：PM2 監聽指定目錄（如 `signal/`），檔案變動觸發自動重啟

### ESM vs CommonJS

- [固] `package.json` 設 `"type": "module"` → 專案預設用 ESM（import/export）
- [固] PM2 設定檔需要 CommonJS 格式，所以用 `.cjs` 副檔名強制 CommonJS 解析
- [固] `.mjs` = 強制 ESM，`.cjs` = 強制 CommonJS，`.js` = 看 package.json 的 type 欄位

### TypeScript 編譯

- [固] `tsc` = TypeScript Compiler，把 `.ts` 編譯成 `.js`
- [固] 編譯流程：`src/*.ts` → `tsc` → `dist/*.js`
- [固] Node.js 不直接跑 TypeScript，需要先編譯（或用 ts-node / tsx 等工具）

### package.json 關鍵欄位

- [固] `"main"` — 套件入口點（如 `dist/index.js`）
- [固] `"scripts"` — npm 指令定義（`npm run build` 等），scripts 內可直接寫 bin 名稱
- [固] `"bin"` — CLI 指令註冊（catclaw 未使用此欄位，直接用 `node catclaw.js`）
- [固] `"type": "module"` — 宣告專案用 ESM
- [固] `"dependencies"` / `"devDependencies"` — 執行期 / 開發期依賴

## 行動

- Wells 專精 C#，Node.js/TS 不熟。解釋時用 C# 類比，跳過基礎但不跳過 Node 生態特有概念
- 遇到 Node.js 生態相關問題，優先查閱此 atom 再回答
- 新學到的 Node/TS 知識持續補充到此 atom
