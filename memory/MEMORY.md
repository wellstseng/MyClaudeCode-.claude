# Atom Index — Global

> 比對 Trigger → Read 對應 atom 檔。

| Atom | Path | Trigger |
|------|------|---------|
| preferences | memory/preferences.md | 偏好, 風格, 習慣, style, preference, 語言, 回應 |
| decisions | memory/decisions.md | 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP |
| spec | memory/SPEC_Atomic_Memory_System.md | 原子記憶規格, atom schema, 記憶系統設計 |
| hardware | memory/hardware.md | 硬體, 電腦, 升級, hardware, PC, GPU, CPU, 顯卡, 記憶體, RAM, 主機板 |
| self-iteration-theory | memory/openclaw-self-iteration.md | 自我迭代, self-iteration, 演進原則, 理論背書, 設計哲學 |
| failures | memory/failures.md | 失敗, 錯誤, debug, 踩坑, pitfall, crash, 重試, retry, workaround |
| toolchain | memory/toolchain.md | 工具, 環境, 指令, command, path, 路徑, bash, git, python, npm, ollama |

---

## 高頻事實

- 使用者: holyl | Windows 10 Pro | 回應語言: 繁體中文
- [固] 原子記憶 V2.6：V2.5 + Self-Iteration Engine（品質函數 + 震盪偵測 + 成熟度模型 + 定期檢閱 + 8 條演進原則）
- [固] Vector Service @ localhost:3849 | Dashboard @ localhost:3848
- [固] Ollama models: qwen3-embedding:0.6b + qwen3:1.7b
- [固] 雙 LLM：Claude Code（雲端決策）+ Ollama qwen3（本地語意）
- [固] Vector DB: ChromaDB（非 LanceDB，因 i7-3770 不支援 AVX2）
