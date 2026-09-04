# wells-design-測試專用成員走internal繞道-runtime-api-乾淨

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: internal, InternalsVisibleTo, 測試專用, public 成員, runtime 乾淨, API 表面, 監控屬性, 測試探針
- Created-at: 2026-08-18

## 知識

- [臨] Wells 裁定（2026-08-18，Coord 案）：若某成員（屬性／方法／參數）開放只是為了讓 UnitTest 抓得到，不得開 public——走繞道，保持 runtime 對外 API 乾淨。
- [臨] tslg-servercore 的標準繞道：成員改 internal，CoreModule.csproj 已有 InternalsVisibleTo（ServerAppXUnitTest／LuaModuleXUnitTest／Titan.Gate.XUnitTest），測試專案直接抓 internal 成員，不需反射。
- [臨] 實例：Coord.IsJoined／Wants／Dialed、CoordServer.MemberCount／PairCount／MembersOf／WantsOf、TitanApp.Coord／CoordRoster 全改 internal（e8088c0）；這類成員註解標「internal：只給測試／監控抓」。

## 行動

- 新增「只給測試用」的成員時一律 internal＋標註用途；發現既有 public 成員僅測試消費時主動收斂
- 新測試專案要抓 internal 時先確認 csproj InternalsVisibleTo 有沒有登記該專案
