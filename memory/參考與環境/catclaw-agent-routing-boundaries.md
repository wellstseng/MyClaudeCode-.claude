# catclaw-agent-routing-boundaries

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: catclaw, project-agent, channel 綁定, boundProject, cron subagent, atom scope, 掛載
- Created-at: 2026-07-02

## 知識

- [臨] catclaw core 無 per-channel agent 路由：ChannelConfig 只有 boundProject 沒有 agentId（src/core/config.ts:24），discord.ts:951 寫死 getBootAgentId()——所有 core 頻道都由 boot agent（defaultAgent=wendy）人格回答；「頻道綁 agent」需 spawn_subagent(agent=) 或核心改造（backlog #7）
- [臨] cron subagent 三缺：execSubagent 不吃 job.agentId（純 metadata）、無 projectId（project namespace recall/atom_write 不通）、allowSpawn:false 寫死（cron.ts:500-560）→ cron task 文字必須自足（檔案絕對路徑直讀直改、不用 atom_write）且 provider 要顯式指定（預設 fallback cron.defaultProvider=gemma）
- [臨] atom scope 靜默降級坑：resolveScopeDir 在 scope=project 但 ctx.projectId 缺失時靜默 fallback 到 global（atom-locations.ts:55-69）；spawn_subagent 不繼承 parent projectId → subagent 裡寫 project atom 會污染 global 層
- [臨] boot 部署 memory root 被 platform.ts:258 強制指向 boot agent 目錄 → project atom 實際落 ~/.catclaw/workspace/agents/{bootAgent}/memory/projects/{basename}/（engine.ts:50 的 ~/.catclaw/agents/{id}/memory 只管 agent-scope）
- [臨] 手動落 atom 檔的完整流程：寫 .md 到 namespace 目錄 + upsert _atom_index.json（trigger-match 的 SSoT）+ 重生 MEMORY.md 鏡像 + POST dashboard /api/memory/resync（餵向量）；resync 不會重建 _atom_index.json
- [臨] hotReload.cron 在 startCron 時評估（cron.ts:289），運行中改 config 不會啟用 watcher → 動 cron 走 dashboard POST /api/cron（in-process 生效+落盤）、POST /api/cron/trigger 手動觸發
- [臨] channel.boundProject 填絕對路徑時，recall 的 projectDir 不正規化（engine.ts:41 直接 join）→ 專案 atom 永不注入頻道問答；resolveBinding 的 basename 推導只作用在 claudeMd/cwd。正確做法：註冊 data/projects/{id}/project.json + boundProject 填 projectId 字串（catclaw core backlog #11，2026-07-02 Phase D 實驗確認修正後 keyword/bm25 命中 project atoms）
- [臨] 驗收「頻道問答吃到專案記憶」不能只看答案對錯——溫蒂靠原始碼回讀也能答對（Phase C 即如此掩蓋 recall 斷鏈）；要開 data/trace-contexts/<日期>/<messageId>.json 的 memoryContext 確認 onboard atom 真的進 context
- [臨] /api/memory/resync 全量向量 seeding 耗時 30+ 分鐘（qwen3-embedding:8b），期間向量服務不可用、recall 降級 BM25+keyword fallback（仍可命中 project atoms）；撞「另一個 resync 進行中」先看 /api/health 的 embedding:ollama.totalSuccess 是否遞增再決定等或重啟
- [臨] Discord 驗收發問要用茉蒂本尊 bot（1320597601506299985，token 在 judy tmux session 的 discord-server process env）走 REST；Claude Code plugin 的 bot（茉蒂claud 1485277122900525086）對專案 parent channel 無 VIEW overwrite 一律 Missing Access；新 thread 須 PUT thread-members 加茉蒂進去
- [臨] CatClaw session 首 turn 會把 memoryContext 凍結成 frozen snapshot（message-pipeline.ts:243，保 prompt cache），之後每 turn 重用不做 live recall——綁定修正/補 atom 後既有 session 吃不到，須 POST /api/sessions/clear {sessionKey} 清空重建（session.ts:225 連 frozen materials 一起清）。Phase D 實測：clear 後下一 turn live recall 注入 4 顆 project atoms（trace-contexts 佐證）

## 行動

- 對 catclaw 掛專案照 MOUNT-SOP「Phase C 實掛修正」段走，不要信原始 config_patch{agentId} 步驟
- 在 cron/subagent 環境設計任務時先確認 projectId/agentId/allowSpawn 三件事的實際傳遞
