# winforms-關閉階段-async-續體不執行-formclosing-殺process必須同步

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: FormClosing, ApplicationExit, fire-and-forget, StopAsync, process 殘留, 關閉不殺, WinForms 關閉, await 續體, Kill, ServerLauncher
- Created-at: 2026-08-20
- Related: dotnet-inline-cant-cross-delegate, failures, wells-design-principles-明碼優先-職責分離-防呆擋非法

## 知識

- [臨] WinForms 關閉階段（FormClosing 之後）訊息迴圈即將結束，UI context 的 await 續體不會再執行：fire-and-forget 呼叫 async 方法只有「第一個 await 之前的同步前綴」會跑，之後的收尾（WaitForExit、writer 關閉、狀態清理）全部蒸發。關閉時的清理必須走全同步路徑（Kill + WaitForExit 專用方法）
- [臨] `Application.ApplicationExit += handler` 寫在 `Application.Run()` 返回「之後」永遠不會觸發（Run 返回時該事件已發完）——備援清理掛勾等於死碼，且不會有任何錯誤訊號
- [臨] FormClosing handler 內的例外會中斷 handler 剩餘邏輯但視窗照樣關閉（CatchException 模式下只寫 log）：清理動作要放在存檔等可能丟例外的步驟「之前」，或各自獨立 try/catch
- [臨] 多個管理項目對同一 exe attach 既有 process 時，若無共用「已接管 PID」名冊，全部會接到同一隻，關閉時其餘實例殺不到；接管失敗被 catch {} 吞掉會讓 UI 顯示已停止 → 使用者再啟動 → 每輪多洩漏一隻（ServerLauncher 4 隻 TitanApp 殘留實案，2026-08-20 修復）
- [臨] 「關閉＝全停」語意的最後保險網：關閉收尾按 exe 完整路徑掃 process 補殺，可蓋掉所有未被追蹤的實例（attach 漏接、前次洩漏）

## 行動

- WinForms 工具要在關閉時殺子 process：寫同步專用 StopForShutdown（Kill+WaitForExit），不得重用 async 停止流程
- review 時看到 Application.Run 之後還有程式碼（尤其事件註冊）→ 直接標死碼
- attach/接管既有 process 的設計：共用 PID 名冊防重複接管 + 失敗必出 log + 關閉時按路徑補殺
