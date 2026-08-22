# doc-程式人員AI協作指南

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: AI協作指南, AI 協作, 協作文件, WorkNote, 團隊指南, AI 最佳實踐, 新人 AI 教育
- Created-at: 2026-06-10
- Related: workflow-icld, cognitive-patterns, toolchain-svn-powershell-中文log編碼

## 知識

- [觀] 《程式人員AI協作指南》正式版位於 C:\Projects\WorkNote\程式人員AI協作指南.md（git: gitlab.uj.com.tw wellstseng/WorkNote，首版 commit f324828，2026-06-10）
- [觀] 用途：Wells 給團隊內程式人員的 AI 協作最佳實踐指南（非強制規範、工具不限），可用於團隊教育/新人導入
- [觀] 結構七章：1 核心原則（責任在使用者＋適用範圍三級嚴格度表＋紅線「轉正即回歸」）、2 心智模型（鋸齒狀能力、語氣≠正確率）、3 任務適配、4 協作循環（含 ICLD 簡介）、5 審查 AI 產出（含 3 個真實案例 📌 框）、6 反模式七條、7 保密邊界；文末 7 條已驗證的外部參考來源
- [觀] 內容雙來源：業界官方指引（Anthropic/GitHub/DORA/SO survey/USENIX/OWASP，2026-06-10 經 WebFetch 驗證）＋ Wells 記憶庫實戰教訓（去識別化：編造規則事件、LINE Bot 誤診、SVN r1155 亂碼）
- [觀] 排版慣例：紅字 <font color="red"> = 違反會出事的紅線；深橘 #C55A11 = 有官方依據的關鍵建議；📌 引用框 = 踩過的坑案例；💡 = 推薦技巧。GitHub/GitLab 會過濾 font color，發布到該平台需改 [!WARNING] 語法

## 行動

- 使用者提到要教團隊用 AI、新人 AI 教育、或要找 AI 協作規範時 → 指向此文件
- 未來新增 AI 協作教訓值得團隊知道時 → 建議 Wells 更新此指南（記得去識別化）
