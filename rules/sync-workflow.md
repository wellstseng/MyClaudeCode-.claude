# 工作結束同步

完成有意義的修改後，主動向使用者提出同步：

> 「這次修改涉及 N 個檔案，要我同步更新 {適用項目} 嗎？」

| 條件 | 同步步驟 |
|------|---------|
| 有 `_AIDocs/` | → 追加 `_CHANGELOG.md`（超 8 筆觸發滾動淘汰） |
| 有新知識/決策/坑點 | → 更新 atom 檔（知識段落 + Last-used） |
| 有 `.git/` | → 秘密洩漏檢查 → `git add` → `git commit` → `git push` |
| 有 `.svn/` | → 秘密洩漏檢查 → `svn add` → `svn commit` |
| 都沒有 | → 僅更新 memory atoms |

適用的步驟都要做完，不要只做一半。

**Workflow Guardian**（`workflow-guardian.py`）自動追蹤修改，未同步時會阻止結束。同步完成後發 `workflow_signal: sync_completed` 解除閘門。
