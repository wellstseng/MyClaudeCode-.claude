# aec-b欄如實載明hook標記退避語不以自評覆蓋

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: anti_evasion_report, 收尾檢核, 退避語, AEC, cross-check, real-evasion
- Created-at: 2026-07-12
- Related: escalation-hook-在-edit-count-proxy-上-false-fire-的辨識無真實失敗迴圈時不盲從不編造

## 知識

- [臨] anti_evasion_report (b) 欄自評「無」若與 hook 偵測記錄矛盾，cross-check 會把 severity 升級 real-evasion（實例：某輪用『非本次』被 Evasion 標記→當輪已補述質問回應，但後續收尾 (b) 仍填「無」→升級）
- [臨] 原則：hook 標記過的措辭不論自判是否實質退避，(b) 一律載明「現象＋處置」；辯解歸當輪質問回應、記錄歸收尾檢核，不得以自評覆蓋 hook 記錄
- [臨] 高風險措辭：「非本次」「不在範圍」「留給未來」——收尾語境全避免；要陳述修補對象不在當前 repo 時，直接寫明對象與層級（如 ~/.claude 基礎設施層＋該處無可修檔），不用範圍推託句式
- [臨] 同型第二犯實例：當輪已答辯過的標記（如時序敍述被字面匹配）收尾時忘記在 (b) 重述→cross-check 仍升級——「已答辯」不等於「免載明」；收尾前必回掃本 session 全部 Evasion 標記（含已答辯項）逐條載明

## 行動

- 收尾提交 anti_evasion_report 前，回掃本 session 有無 hook Evasion 標記；有則 (b) 必載明現象＋處置
