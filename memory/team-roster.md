# 程式團隊名冊

- Scope: global
- Confidence: [固]
- Trigger: 團隊, 名冊, 成員, SVN帳號, Discord ID, Redmine ID, 暱稱
- Last-used: 2026-03-27
- Confirmations: 18
- Related: redmine-config, discord-channels, hot-topics, project-ecosystem

## 知識

### 查詢方式
- [固] 資料位置：~/.catclaw/workspace/data/team.sqlite
- [固] 查詢腳本：node scripts/query-team.mjs
- [固] Schema：members(id, name, job, redmine_id, svn_account, discord_acc_id, nick_names)

### 成員一覽（15 人）

| id | name | nick_names | svn_account | discord_acc_id | redmine_id |
|----|------|------------|-------------|----------------|------------|
| 1 | 曾煒智 | 小白,Wells | wellstseng | 480042204346449920 | 157 |
| 2 | 陳煜閎 | 阿光 | holylight | 831783571513278464 | 146 |
| 3 | 李志鵬 | 志鵬 | lucas0812 | 906080408637173780 | 147 |
| 4 | 林世軒 | QQ | bill56 | 280546383424126977 | 70 |
| 5 | 邱凱聖 | 凱聖,仔仔 | ccjh20741 | 751374872491458622 | 145 |
| 6 | 李若綱 | 若綱 | roy2991 | 590027011423207455 | 211 |
| 7 | 曾羿華 | 華仔,羿華 | yihua0812 | 741308951660068955 | 142 |
| 9 | 曾慶豐 | 慶豐 | allan110223 | 801391235750297611 | 224 |
| 12 | 鄭迪升 | 迪升 | dison0725 | 629964832413843457 | 227 |
| 13 | 黃群互 | 群互,Cell | gn02288889 | 1404284398144061540 | 226 |
| 14 | 李國維 | 國維 | glwillie99 | 1347581719917887518 | 231 |
| 15 | 郭展源 | 展源 | circle0910 | 619395315245645846 | 136 |
| 16 | 陳威霖 | Try | lalatry724 | 745233652484538410 | 148 |
| 17 | 詹士賢 | 小賢 | superjns | 906062826349666305 | 149 |
| 18 | 林子平 | 子平 | deven00 | 906081339630059523 | 152 |

## 行動

- CR 指派時用 SVN 帳號查 redmine_id
- 需要 @ Discord 成員時用 discord_acc_id
- 找不到對應時 fallback 到 bot 帳號（wellsaibot, redmine_id=235）
