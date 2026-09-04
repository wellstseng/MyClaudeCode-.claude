# feedback-移植轉寫類任務-忠實1比1-勿擅自對齊他版權威或加料

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: 移植, 改成C#, 轉寫, port, rewrite, 翻譯腳本, python 轉 C#, 忠實移植, 1:1, 路徑不要動, 全部維持
- Created-at: 2026-09-04
- Related: wells-workflow-copilot-not-driver, feedback-workflow-discipline

## 知識

- [臨] 使用者說「把 X 改成 Y 語言/形式」＝忠實 1:1 轉寫：模板、路徑、流程、輸出佈局、甚至怪癖格式全部維持原樣；唯一可動的是實作語言本身與該語言不可行處的最小替代（如 JsonMapper 綁 ILRuntime → 換 JsonReader）。
- [臨] 2026-09-04 rtgen.py→C# 實例：AI 探勘後發現「更新的權威版本」（RpcGenWeb 模板）與現行落位不同，擅自升級成對齊新模板＋改輸入輸出路徑＋加 server 端產出＋csproj 檢查，被使用者糾正「我只說改 python 腳本到 C#，路徑不要動，全部維持」後整檔回退重寫。

## 行動

- 轉寫/移植任務動手前自問：每一處與原版的差異，是「目標語言不可行」還是「我覺得更好」？後者一律不做，最多在收尾報告提一句建議。
- 探勘發現生態已演化（現行檔案與待移植腳本不一致）→ 先回報差異讓使用者選基準，不擅自替使用者選「較新的權威」。
