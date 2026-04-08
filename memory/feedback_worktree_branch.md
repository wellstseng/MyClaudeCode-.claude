# 功能開發前詢問 Git Worktree

- Confidence: [固]
- Related: workflow-rules

## 知識

- [固] 進行功能開發、優化、或擴充功能之前，必須先詢問使用者是否需要開一條 git worktree (branch) 進行作業
- **Why:** 使用者希望功能開發與主線隔離，避免半成品汙染 main branch，也方便 review 和回滾
- **How to apply:** 當判斷即將開始的工作屬於「新功能」「功能優化」「功能擴充」時（不含 bugfix hotfix、文件修改、記憶/atom 維護），在動手寫程式碼前主動問：「這次要開 git worktree/branch 作業嗎？」使用者同意則建立 worktree + branch，拒絕則直接在當前分支作業，本 session 不再重複詢問。
