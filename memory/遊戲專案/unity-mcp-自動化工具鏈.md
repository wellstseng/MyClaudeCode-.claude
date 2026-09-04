# Unity MCP 自動化工具鏈

- Scope: global
- Confidence: [固]
- Trigger: unity-mcp, Unity重編, Unity recompile, refresh_unity, AssetDatabase.Refresh, Unity自動化, batchmode, Unity MCP
- Last-used: 2026-04-23
- Confirmations: 2
- Related: toolchain, project-ecosystem, unity-mcp-setup (_AIDocs/Tools)

## 知識

- [固] Unity MCP server: CoplayDev/unity-mcp (8.6k stars)，Unity Editor plugin + HTTP server
- [固] 安裝方式：manifest.json 加 "com.coplaydev.unity-mcp": "https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#main"
- [固] Claude Code MCP 設定：~/.claude.json → "unity-mcp": { "type": "http", "url": "http://localhost:8080/mcp" }（全域）
- [固] **`type` 欄位必填**（2026-04-23 踩過）：漏 `"type": "http"` 則 Claude Code 不知 transport，server 靜默不載入；完整 SOP 見 _AIDocs/Tools/unity-mcp-setup.md
- [固] 健康檢查：`curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/mcp` → 回 `406` 即 server 活著（協定不對但 port 通）
- [固] 前提：Unity Editor 必須開著且載入專案，plugin 才會跑 HTTP server
- [固] 關鍵 tool: refresh_unity — 呼叫 AssetDatabase.Refresh() 觸發 script 重新編譯
- [固] 工作流：改完 .cs → 呼叫 refresh_unity → Unity 重編主程式 DLL → msbuild hotfix 專案
- [固] 備用方案（Unity 沒開時）：batchmode CLI → "C:/Program Files/Unity/Hub/Editor/2022.3.62f3/Editor/Unity.exe" -batchmode -quit -nographics -projectPath "C:/Projects/TSLG/Develop/Client" -logFile -
- [固] 限制：batchmode 與已開的 Editor 互斥（同一專案只能一個 Unity instance）

## 行動

- 修改 Unity .cs 檔後需要觸發重編 → 檢查 unity-mcp 是否 connected → 是則呼叫 refresh_unity → 否則提示使用者開 Unity 或用 batchmode
- hotfix 專案 build 失敗且錯誤是 '找不到 XXX 的定義' → 通常是主程式 DLL 沒重編，先 refresh_unity
