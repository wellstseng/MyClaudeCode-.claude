# Hotfix ILRuntime 陷阱

- Confidence: [固]
- Related: preferences, toolchain

## 知識

### `#if UNITY_EDITOR` 在 hotfix 無效（不能作執行期開發旗標）

- [固] ILRuntime hotfix DLL 由**獨立 csproj** 編譯（例：`BRM_ILR_Hotfix/BRM.ILR.HotFixProj.csproj`），`DefineConstants` 是**編譯時固定**，編出 DLL 後分支已固化
- [固] hotfix csproj 常把 `UNITY_EDITOR` 寫死在 Release `DefineConstants`（為了反射主工程 Editor 型別），所以 hotfix 內的 `#if UNITY_EDITOR` 不會跟著 Unity 真實環境（Editor Play vs Built Player）切換
- [固] 要執行期區分 Editor/Player → 用 `UnityEngine.Application.isEditor`（runtime property），**不要** 用 `#if UNITY_EDITOR`
- [觀] 同理所有 `#if` 預處理指令（`#if DEBUG` / `#if DEVELOPMENT_BUILD` / 自訂 symbol）在 hotfix 皆受此限制，若需執行期切換一律改 runtime 判斷

## 行動

- 在 hotfix（`*_ILR_Hotfix/` 或 `Hotfix*.csproj` 內的 .cs）寫 code 時，若需要「僅 Editor 生效」的分支 → **用 `if (Application.isEditor)`**
- 相反情境（想要 Editor-only 編譯進 DLL 的 dev 輔助）：csproj `DefineConstants` 搭配 `#if` 仍可用，但要清楚理解「DLL build 後分支已固化」
- 當發現 hotfix 內 `#if UNITY_EDITOR` 邏輯在 Player build 也生效、或 Editor Play 沒生效時 → 立即改 runtime 判斷，不要重 build 搏運氣
