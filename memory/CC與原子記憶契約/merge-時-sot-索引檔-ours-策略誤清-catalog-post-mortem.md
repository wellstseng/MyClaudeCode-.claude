# merge-時-SoT-索引檔-ours-策略誤清-catalog-post-mortem

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: catalog 誤清, _INDEX.md 被刪, index 磁碟不一致, SoT 衝突解, _atom_index.json merge, sync-memory-index, atoms 隱形, 衝突檔 ours, 衍生索引, post-mortem
- Created-at: 2026-07-06
- Related: upstream-merge-mac-適配工作流, decisions-architecture, feedback-memory-structure

## 知識

- [臨] 始末：2026-07-06 merge upstream 時 _atom_index.json 取 ours（當作個人資料衝突解）→ upstream 53 顆 atom 檔進磁碟但不在 index → 後續 atom_write 觸發 _trigger_sync_memory_index() → sync-memory-index.py 以 index 為 SoT 渲染 → 9 個 per-level _INDEX.md 被清空刪除、atoms 從注入管線隱形。發現途徑：commit 輸出意外的 D 檔——非主動驗證抓到，屬幸運
- [臨] 根因：把 index 檔當單純「個人資料」解衝突，忽略其雙面身份——既含本地登記（個人）又是磁碟狀態的衍生索引（共享不變式）；ours/theirs 二選一都破壞「index↔磁碟一致」不變式。更深層：merge 審查只盯衝突檔，沒審「非衝突但語意耦合」檔群（atoms 檔案 vs 登記它們的 index）
- [臨] 設計原理：sync-memory-index.py 刻意不回讀磁碟、純從 _atom_index.json 渲染 catalog（MEMORY.md/_local_catalog.md/per-level _INDEX.md）——避免磁碟掃描歧義、配合 SessionStart 0-atom fail-loud。所以「登記缺 = 渲染空 = 刪檔」是正確行為，斷點在 merge 策略破壞了它的前置條件
- [臨] 最終正解：SoT/索引類檔案的 merge 不是選邊而是「按鍵合成」——以 name 為 key，本地同名優先（保個人版本/路徑）、只收磁碟存在檔（防幽靈登記），合完立刻 regen + 雙向對帳
- [臨] 防再犯：(1) merge 後驗證清單加「索引↔磁碟雙向對帳」（index 條目檔案存在？磁碟 atom 有登記？） (2) 衝突清單見 _atom_index.json/_ATOM_INDEX.md/MEMORY.md → 觸發合成流程非 ours (3) 同名 atom 兩邊路徑可能不同（upstream 已 realm 遷移），合成必以 name 為 key 非 path

## 行動

- merge 見索引/SoT 檔衝突 → 按鍵合成（本地優先+磁碟存在才收），禁 ours/theirs 整檔選邊
- merge 後對帳：index 條目↔磁碟檔案雙向驗證再 commit
- commit 前審 git status 的意外 D/A 檔——自動機制副作用的第一現場
- 改動共享不變式前先找出讀它的自動機制（本例：atom_write → fire-and-forget sync）
