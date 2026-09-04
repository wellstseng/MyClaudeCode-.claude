# feedback-註解一律白話-不堆術語

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: 註解, comment, 白話, 術語, summary 註解, 程式註解, doc comment
- Created-at: 2026-08-22
- Related: feedback-收尾報告使用者視角四要素-白話綜觀非片段細節, preferences

## 知識

- [觀] Wells 明確要求：程式註解（含 /// summary、Lua 註解）一律用白話、簡單易懂的方式寫，不要堆術語（2026-08-22 uuid 直綁改動中當面糾正）。
- [觀] 術語密度高的註解（「借用協定」「blittable」「RFC 4122 v4」連發）是反例；正例是先講「發生什麼事、為什麼」，術語只在必要時點到（例：「Lua 先準備好 37 bytes 的空間傳進來，C# 只負責填字——兩邊各管各的記憶體」）。

## 行動

- 寫任何註解前用讀者視角自檢：不懂內部代號的人能否一次讀懂；術語首次出現補一句白話
- 既有註解風格偏術語時，新增註解仍以白話為準（本偏好優先於「跟隨周邊風格」）
