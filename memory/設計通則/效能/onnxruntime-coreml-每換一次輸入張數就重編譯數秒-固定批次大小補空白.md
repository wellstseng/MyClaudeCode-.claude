# onnxruntime-coreml-每換一次輸入張數就重編譯數秒-固定批次大小補空白

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: onnxruntime, CoreML, CoreMLExecutionProvider, 推論變慢, batch, 動態批次, 人臉辨識, Apple Silicon
- Created-at: 2026-11-03
- Source: session:164208c3#a79a3d07 2026-11-03

## 知識

- [臨] onnxruntime 1.19 在 Mac 用 CoreMLExecutionProvider 時，每次輸入的批次張數和上一次不同，就要重新編譯 2.5～4 秒，而且只記得最後一種張數（16→7→16 第三次又慢）。張數固定時一批只要約 0.03 秒，比純 CPU 快十幾倍。
- [臨] 解法：固定每批 N 張（例如 16），不足的補零、超過的切塊，跑完只取前面真的那幾列。實測 ArcFace w600k_r50：每張照片的臉數 1～20 不一，沒固定時一張照片要 1.4 秒，固定後 0.15 秒。
- [臨] CoreML 與 CPU 算出的特徵 cosine 至少 0.998，可以混用同一批資料。

## 行動

- Mac 上用 onnxruntime 跑 CoreML 而且輸入張數會變時，先寫固定批次＋補空白，再量速度
