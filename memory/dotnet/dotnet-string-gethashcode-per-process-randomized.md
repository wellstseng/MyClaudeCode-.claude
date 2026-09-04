# dotnet-string-gethashcode-per-process-randomized

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: GetHashCode, hash 路由, hash 釘定, FNV, consistent hashing, 後端路由
- Created-at: 2026-07-02

- Related: dotnet-xunit-getentryassembly-testhost

## 知識

- [臨] .NET Core 起 string.GetHashCode 每行程隨機化(hash seed randomization),不可用於跨行程/跨機器需一致的 hash 路由——多台 Gate 用它做 hash(entityUid)%n 釘後端會各釘各的,同 entity 落不同後端
- [臨] 需穩定分流時自寫確定性 hash(如 FNV-1a 32-bit:h=2166136261,逐 char h=(h^c)*16777619)。orbit Gate S6 的 GateSvr.MapBackendIndexOf 即此做法,public static 供測試對算落點

## 行動

- （依知識內容判斷）
