# vMLX × Gemma 4 31B Abliterated 本地化嘗試（暫停）

- Scope: global
- Confidence: [臨]
- Type: experience
- Trigger: vmlx, gemma4, gemma 4, abliterated, dealignai, 破解版模型, 去審查模型, JANG, 本地 LLM, mac 跑大模型, ollama, gguf, windows, rdchat, RTX 3090, douyamv, 31B JANG
- Created: 2026-05-22
- Related: toolchain-ollama, toolchain

## 緣由

- 2026-05-22 使用者貼 Patreon 文章 `https://www.patreon.com/posts/154988822`，要求裝 Gemma 4 破解版
- 來源模型：`dealignai/Gemma-4-31B-JANG_4M-CRACK`（HuggingFace 公開，Abliteration 技術：矩陣正交化拔掉 refusal vector）
- 引擎：vMLX（**不能用 Ollama，作者明確說 Ollama/標準 mlx_lm 不支援 Gemma 4**）

## 已完成的環境（保留可用）

- [臨] `brew install uv` → uv 0.11.15
- [臨] `uv tool install vmlx` → vmlx_engine 1.5.46
- [臨] `uv tool install huggingface_hub` → hf CLI 1.16.0
- [臨] `~/.zshrc` 已加：`export PATH="$HOME/.local/bin:$PATH"`
- [臨] `~/.zshrc` 有 `HF_TOKEN`（使用者已 revoke，要再啟用需生新 token）
- [臨] **模型已下載完整 21 GB**：`~/.cache/huggingface/hub/models--dealignai--Gemma-4-31B-JANG_4M-CRACK`（5 個 safetensors shard + tokenizer + jang_config）

## 失敗原因（[臨]，單次觀察）

- [臨] M4 / 32 GB Mac 啟動 `vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080`，wired memory limit 27 GB（模型 23 GB），加上系統其他應用就**系統當機重啟**
- [臨] 文章宣稱「24 GB+ 即可」是理論值；**32 GB 機跑 31B JANG_4M 是邊緣值，實務不可行**
- [臨] 卡點位置：vmlx log 停在 `Wired limit set to 27 GB (model 23 GB)` 之後 8 分鐘無進度，最終整機當機

## 續行方向（待使用者決定）

- [臨] 路線 A：清空背景應用（瀏覽器/IDE/CatClaw）騰出 ≥27 GB → 重啟 vmlx。仍邊緣，可能再當
- [臨] 路線 B：**換更小的 abliterated 模型**（Gemma 3 12B-abliterated / Qwen 2.5 14B-abliterated，wired ~8-10 GB），32 GB 機綽綽有餘 ← **建議**
- [臨] 路線 C：丟到 rdchat（RTX 3090, 24 GB VRAM）跑 31B Q4，但 rdchat 走 Ollama backend，需確認該模型有 Ollama gguf 版本

## 重啟指令（如選 A）

```bash
export PATH="$HOME/.local/bin:$PATH"
export HF_TOKEN="hf_新token"
vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080
curl http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" \
  -d '{"model":"local","messages":[{"role":"user","content":"你好"}],"stream":false}'
```

## Windows + Ollama gguf 路線（2026-05-23 實機驗證）

- [觀] **背景**：Mac vmlx 路線因 32GB RAM 邊緣值放棄；Windows 改走 Ollama + 社群 gguf 量化版
- [觀] **唯一已實機驗證能跑的來源**：`juilpark/gemma-4-31B-it-uncensored-heretic:q4_k_m`（**Wells 2026-05-23 親測 Windows + Ollama 0.24.0 可用**）

### 安裝指令（已驗證）

```powershell
# 1. 裝 Ollama for Windows
winget install Ollama.Ollama

# 2. 拉已驗證版本（從 ollama.com library，**沒有 hf.co/ 前綴**，tag 用小寫）
ollama run juilpark/gemma-4-31B-it-uncensored-heretic:q4_k_m
```

### 失敗來源紀錄（**不要重踩**）

| 來源 | 問題 | 根因 |
|------|------|------|
| `hf.co/douyamv/Gemma-4-31B-JANG_4M-CRACK-GGUF:Q4_K_M` | 模型 collapse，輸出 `l l l l...` / `---` / `S-S-S-` | 從 dealignai 的 MLX JANG_4M 轉 gguf，中間 dequant→requant weights 崩 |
| `hf.co/llmfan46/gemma-4-31B-it-uncensored-heretic-GGUF:Q4_K_M` | `Error: 400`（build 階段失敗） | 不明，server.log 沒抓到 error，Ollama 0.24.0 + 該 repo metadata 不相容 |

### 關鍵知識

- [觀] **不要從 dealignai/JANG 系列衍生的 gguf 開始**——所有從 MLX JANG_4M 轉的 gguf weights 都會崩，徵兆是「輸出連續同字」（`l l l...` / `---`）
- [觀] **直接從 `google/gemma-4-31b-it` 做 abliteration / heretic 的 gguf 才可用**——但要實測，不是每個都能在 Ollama build 成功（llmfan46 就 build 400）
- [觀] **Ollama 0.24.0 對 Gemma 4 + 某些 community gguf metadata 有相容性問題**，build 階段直接 400 但 server.log 沒抓到 error 訊息
- [觀] **Ollama 官方 library 有 `gemma4`（26b/31b，9.9M pulls）但只有審查版**，破解必須走社群
- [觀] tag 命名：`juilpark` 是 ollama.com library 上的 community member（用 `:q4_k_m` 小寫），HuggingFace 來源用 `hf.co/{repo}:{Q4_K_M}` 大寫
- [觀] 不需要 HF_TOKEN（公開 repo）

## 卸載指令（如完全放棄）

```bash
rm -rf ~/.cache/huggingface/hub/models--dealignai--Gemma-4-31B-JANG_4M-CRACK  # 釋放 21 GB
uv tool uninstall vmlx huggingface_hub
brew uninstall uv
# 手動清 ~/.zshrc 的 PATH 與 HF_TOKEN 那兩行
```

## How to apply

- 使用者再次提及 vmlx / abliterated / Gemma 4 破解 → 注入本 atom，提醒：模型已下載完整在本機、不要重抓
- 若要重啟，先 free memory check（vm_stat），確認 ≥27 GB free 再 serve
- 推薦路線 B（小模型 abliterated），別硬上 31B
