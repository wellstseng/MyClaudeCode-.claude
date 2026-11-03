# 兒童人臉辨識-opencv-sface-分不清小孩-改用-arcface-w600k_r50-並用同照片不同人當反例定門檻

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: 人臉辨識, 人臉分群, face recognition, SFace, ArcFace, insightface, 小孩照片, 門檻校準
- Created-at: 2026-11-03
- Source: session:164208c3#a79a3d07 2026-11-03

## 知識

- [臨] OpenCV 內建 SFace 特徵對幼兒園小朋友幾乎分不開：同一張照片裡的兩個不同小孩有 32% 相似度超過官方同人門檻 0.363。InsightFace w600k_r50（ArcFace，buffalo_l.zip 內）降到 6%，分群幾乎一群一個小孩。
- [臨] 沒有標註資料時的反例來源：同一張照片裡的兩張臉一定是不同人。用它量「別人被當成他」的比例來定門檻，也用「同群在同照片出現兩次」量分群純不純。
- [臨] 實測參數（ArcFace、average linkage cosine）：分群距離 0.65；像不像取記下的臉裡最像 5 張的平均，0.55 時同照片其他小孩只剩 0.2% 過關、0.48 時 4%。

## 行動

- 做小孩的人臉辨識時不用 SFace，直接用 ArcFace
- 定門檻前先用同照片不同人量誤認率
