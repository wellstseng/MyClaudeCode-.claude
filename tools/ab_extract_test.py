# ONE-OFF: 一次性測試腳本，非常規工具
"""
ab_extract_test.py — A/B 萃取品質驗證：rdchat (qwen3.5) vs local (qwen3:1.7b)

用法：python3 tools/ab_extract_test.py
"""

import json
import sys
import time
from pathlib import Path

# 讓 import 找到同目錄的 ollama_client
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ollama_client import get_client  # noqa: E402

CLAUDE_DIR = Path.home() / ".claude"

# ── Transcript 讀取（搬自 extract-worker）──────────────────────────────────

def extract_assistant_texts(transcript_path: Path, max_chars: int = 20000):
    texts, total = [], 0
    with open(transcript_path, "r", encoding="utf-8") as f:
        for raw in f:
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "assistant":
                continue
            content = obj.get("message", {}).get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    t = block.get("text", "")
                    if t and len(t) > 30:
                        texts.append(t)
                        total += len(t)
            if total >= max_chars:
                break
    return texts

# ── Prompt 組裝（搬自 extract-worker）──────────────────────────────────────

_SYSTEM_CONTEXT = (
    "你是「原子記憶系統」的知識萃取器。萃取出的知識會存入長期記憶，供未來 session 引用。\n"
    "只萃取「這個專案/環境特有的」、「下次會用到的」事實。通用程式知識不要。\n\n"
)
_FORMAT_SPEC = (
    "輸出 JSON array: [{\"content\": \"精簡事實，最多150字\", "
    "\"type\": \"factual|procedural|architectural|pitfall|decision\"}]\n\n"
    "範例（值得萃取）:\n"
    '  {"content": "rdchat Open WebUI LDAP 端點是 /api/v1/auths/ldap，用 user 欄位（非 email）", "type": "factual"}\n'
    '  {"content": "GTX 1050 Ti 跑 qwen3:1.7b generate 約 30s，qwen3-embedding embed 約 5s", "type": "factual"}\n'
    '  {"content": "LanceDB search 用 cosine metric，min_score 0.65 以下多為噪音", "type": "architectural"}\n\n'
    "範例（不要萃取）:\n"
    '  ✗ "Python 的 dict 是 hash table" → 通用知識\n'
    '  ✗ "修改了 config.py 第 43 行" → session 進度，不是知識\n'
    '  ✗ "使用 git commit 提交變更" → 常識\n\n'
)
_RULES_COMMON = (
    "規則:\n"
    "- 只萃取此專案/環境特有的具體事實（含數值、路徑、版本、錯誤碼）\n"
    "- 跳過：程式碼片段、session 進度、隨便 Google 就能查到的知識\n"
    "- 沒有值得萃取的內容就輸出 []\n"
    "- 直接輸出 JSON，不要解釋\n"
    "/no_think\n\n"
)

def build_prompt(intent: str, text: str) -> str:
    intent_lines = {
        "build": "本次 session 類型：開發建構。重點關注：架構決策、工具配置、框架行為、API 特性。\n\n",
        "debug": "本次 session 類型：除錯。重點關注：根因分析、錯誤模式、誤導性症狀、環境相關的坑。\n\n",
    }
    line = intent_lines.get(intent, intent_lines["build"])
    return _SYSTEM_CONTEXT + line + _FORMAT_SPEC + _RULES_COMMON + f"Session 文字:\n{text[:4000]}\n\nJSON:"

# ── 直接打特定 backend ─────────────────────────────────────────────────────

def call_backend_directly(client, backend_name: str, prompt: str,
                          timeout: int = 120, think: bool = False):
    """繞過 _pick_backend，直接打指定 backend。"""
    backend = None
    for b in client._backends:
        if b.name == backend_name:
            backend = b
            break
    if not backend:
        return None, 0.0

    payload = {
        "model": backend.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": think,
        "options": {"temperature": 0.1, "num_predict": 2048},
    }
    t0 = time.time()
    result = client._do_request(backend, "/api/chat", payload, timeout)
    elapsed = time.time() - t0
    if result is None:
        return None, elapsed
    return result.get("message", {}).get("content", ""), elapsed

# ── JSON 解析 ─────────────────────────────────────────────────────────────

def parse_json_response(raw: str):
    """嘗試從 LLM 回應中解析 JSON array。"""
    if not raw:
        return None, "empty response"
    # 清理常見問題
    text = raw.strip()
    # 找 JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return None, "no JSON array found"
    try:
        arr = json.loads(text[start:end+1])
        if isinstance(arr, list):
            return arr, None
        return None, "parsed but not a list"
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"

# ── 品質分析 ───────────────────────────────────────────────────────────────

def analyze_items(items):
    """分析萃取項目品質。"""
    if not items:
        return {"count": 0, "avg_length": 0, "type_dist": {}, "specificity": "0/0"}
    types = {}
    lengths = []
    specific_count = 0  # 含數值/路徑/版本的具體項目
    for item in items:
        t = item.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
        c = item.get("content", "")
        lengths.append(len(c))
        # 具體性判斷：含數字、路徑、版本號
        if any(ch.isdigit() for ch in c) or "/" in c or "\\" in c or "." in c:
            specific_count += 1
    return {
        "count": len(items),
        "avg_length": sum(lengths) / len(lengths),
        "type_dist": types,
        "specificity": f"{specific_count}/{len(items)}",
    }

# ── Main ──────────────────────────────────────────────────────────────────

def main():
    # 測試用 transcript
    transcript = Path(CLAUDE_DIR / "projects/c--Projects/2cd81148-8aa1-4926-98c9-d2aa352c44e1.jsonl")
    if not transcript.exists():
        print(f"Transcript not found: {transcript}")
        sys.exit(1)

    print(f"=== A/B 萃取品質驗證 ===\n")
    print(f"Transcript: {transcript.name}")

    # 讀取文字
    texts = extract_assistant_texts(transcript)
    merged = "\n---\n".join(texts)
    print(f"Assistant 文字區塊: {len(texts)} 個, 共 {len(merged)} 字元")
    print(f"送入 prompt 的文字: {min(4000, len(merged))} 字元\n")

    # 組 prompt（用 build intent 測試）
    prompt = build_prompt("build", merged)

    # 初始化 client
    client = get_client()
    print(f"Backends: {[b.name for b in client._backends]}\n")

    # 測試組合: (label, backend_name, think)
    test_configs = [
        ("rdchat-think", "rdchat", True),
        ("rdchat-nothink", "rdchat", False),
        ("local-nothink", "local", False),
    ]

    results = {}
    for label, name, think in test_configs:
        print(f"--- {label} (think={think}) ---")
        raw, elapsed = call_backend_directly(client, name, prompt, timeout=300, think=think)
        if raw is None:
            print(f"  第一次失敗，重試...")
            raw, elapsed = call_backend_directly(client, name, prompt, timeout=300, think=think)
        if raw is None:
            print(f"  失敗！跳過。")
            results[label] = {"error": "request failed"}
            continue

        print(f"  回應時間: {elapsed:.1f}s")
        print(f"  原始回應長度: {len(raw)} 字元")
        if len(raw) < 50:
            print(f"  原始回應: {repr(raw)}")

        items, err = parse_json_response(raw)
        if err:
            print(f"  JSON 解析失敗: {err}")
            print(f"  原始回應前 500 字: {raw[:500]}")
            results[label] = {"error": err, "raw": raw[:1000], "elapsed": elapsed}
            continue

        analysis = analyze_items(items)
        analysis["elapsed"] = elapsed
        analysis["items"] = items
        results[label] = analysis
        print(f"  萃取項目數: {analysis['count']}")
        print(f"  平均長度: {analysis['avg_length']:.0f} 字")
        print(f"  具體性: {analysis['specificity']}")
        print(f"  type 分布: {analysis['type_dist']}")
        print()

    # ── 輸出對比表 ──
    labels = [l for l, _, _ in test_configs]
    header_labels = {
        "rdchat-think": "rdchat think=T",
        "rdchat-nothink": "rdchat think=F",
        "local-nothink": "local think=F",
    }
    print("\n=== 對比表（Markdown）===\n")
    h = " | ".join(header_labels.get(l, l) for l in labels)
    print(f"| 維度 | {h} |")
    print("|------|" + "|".join("---" for _ in labels) + "|")

    for dim, key in [
        ("JSON 格式正確", None),
        ("回應時間", "elapsed"),
        ("萃取項目數", "count"),
        ("平均 content 長度", "avg_length"),
        ("具體性", "specificity"),
        ("type 分布", "type_dist"),
    ]:
        vals = []
        for label in labels:
            r = results.get(label, {})
            if "error" in r:
                vals.append(f"FAIL: {r['error'][:30]}")
            elif key is None:
                vals.append("OK" if "items" in r else "FAIL")
            elif key == "elapsed":
                vals.append(f"{r.get(key, 0):.1f}s")
            elif key == "avg_length":
                vals.append(f"{r.get(key, 0):.0f} 字")
            else:
                vals.append(str(r.get(key, "N/A")))
        print(f"| {dim} | " + " | ".join(vals) + " |")

    # ── 輸出各 backend 萃取內容 ──
    print("\n=== 萃取內容明細 ===\n")
    for label in labels:
        r = results.get(label, {})
        items = r.get("items", [])
        print(f"### {label} ({len(items)} 項)")
        for i, item in enumerate(items, 1):
            print(f"  {i}. [{item.get('type', '?')}] {item.get('content', '')}")
        print()

    # 存原始結果到 _staging
    staging = CLAUDE_DIR / "memory" / "_staging"
    staging.mkdir(parents=True, exist_ok=True)
    out_path = staging / "ab_extract_results.json"
    serializable = {}
    for label in labels:
        r = dict(results.get(label, {}))
        serializable[label] = r
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"\n原始結果已存: {out_path}")


if __name__ == "__main__":
    main()
