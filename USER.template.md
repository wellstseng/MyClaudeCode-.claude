# USER.template.md - 操作者設定範本

> 新使用者首次啟動 session 時，hook 會自動複製此檔為 `USER-{username}.md`，
> 再生成 `USER.md`（gitignored）供 CLAUDE.md @import。
> 請勿直接編輯 USER.md，改你自己的 `USER-{username}.md`。

## 基本資料

- **帳號**：**取自此電腦登入後的系統使用者名**
- **平台**：Windows 11 Pro

## 溝通偏好

- **回應語言**：繁體中文（技術術語可英文）
- **輕量極簡**：偏好直接、低抽象的解法，不用不需要的框架
- **高可讀性**：一個檔案看完相關邏輯，減少跨檔跳轉
- **不自動產生文件**：不主動建立 README / 文件，除非明確要求
- **Prompt 輸出**：給使用者複製貼上的 prompt，一律包在 code block 裡
- **縮寫指令**：「上GIT」「執P」等定義見 `memory/preferences.md`

## 決策偏好

- 需要決策時：**詳細綜觀 + 分析條列 + 建議優選**
- 大型計畫：分階段 session 執行，每階段完成 + 驗證 + 上傳 GIT 後，提供下一階段 prompt
