# wells-design-principles-明碼優先-職責分離-防呆擋非法

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: 設計原則, 明碼, 反直覺, 隱性語意, 哨兵值, 職責分離, 反射掃描, magic value, 註冊表, 防呆, 開發文化, design principle
- Created-at: 2026-07-28
- Related: wells-workflow-copilot-not-driver, decisions-architecture, preferences, coremodule-entry-assembly-拓撲前提地雷-orbit-tslg同dna

## 知識

- [臨] 明碼優先於慣例/反射：型別發現、註冊這類「編譯期已知答案」的問題，用看得見的資料結構（Dictionary/List/static readonly 清單）解，不用執行期掃描。反射掃 assembly 被視為：浪費啟動效能 + 靜默失敗源 + Find All References 失明（隱關聯）。實例：TSLG 模組註冊 attribute+GetEntryAssembly 掃描 → Defines 明碼清單（2026-07-28）
- [臨] 欄位名即語意：不接受欄位背負隱藏職責。「不熟專案的人看到欄位名就該懂它管什麼」是硬標準。實例：DataId 兼職「存不存 DB」判斷（==0 哨兵值）被裁定反直覺 → 拆出 SaveToDB/IsPersistent，DataId 只當 DB key
- [臨] 非法組合用驗證 throw 擋、不用哨兵魔術值容忍：「更嚴謹的區分職責，用判斷來擋掉不該出現的設定」。冗餘欄位+驗證 > 單欄位雙語意。throw 訊息要指名類別/欄位
- [臨] 結構上使錯誤不可能 > 執行期容忍：DataId 撞號用 Dictionary key 唯一性 + 進場 throw 雙保險；「id=0 可重複」這種例外規則被否決
- [臨] 化繁為簡直覺：拒 Source Generator（多養 Roslyn 黑盒）、拒雙清單設計，選單一清單 + flag。口頭禪式判準「理論上可以降階成資料結構定義、runtime 帶入吧」——優先考慮最平凡的 C# 寫法
- [臨] 追根源文化：接受方案前會追「為什麼原設計這樣做」（如 Orbit 為何用反射）；答案若是「歷史慣性/時代慣例」而非主動選擇，改起來不手軟
- [臨] 協作模式：AI 給方案 → Wells 自己動手改一版 → 丟回「我改了一版你看一下」要求 review。review 要抓真 bug（他的版本曾有 DataId 撞號/漏賦值），不是橡皮圖章；改完要求「重新檢查邏輯行為是否跟之前不一樣」= 行為等價性驗證（golden diff 等級）

## 行動

- 設計/重構方案先過這組濾網：有沒有隱性語意、哨兵值、執行期解編譯期問題
- 提案時優先給最平凡的資料結構解，框架/工具鏈方案（SG、DI container）需明確收益佐證
- Wells 自改版本回來 review 時，用機器驗證（golden diff/編譯/grep 稽核）抓等價性，不憑目視
