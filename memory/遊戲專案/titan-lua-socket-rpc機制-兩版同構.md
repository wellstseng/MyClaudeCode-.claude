# titan-lua-socket-rpc機制-兩版同構

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: titan, gate, proxy, goo_rpc, goo_gate, lua socket, lua連線, entities.lua, rpc機制, fire-and-forget, channel pull, titan_net_id
- Created-at: 2026-07-15
- Related: orbit-hotfix-lua-direction, titan-dotnet-split, lua-bridge, dotnet-interface-devirt-pgo, titan-c-port-是-titan-行為的現成權威來源勿從零重寫, luajit-ffi-函式指標型別三種等價寫法-ctype相等比較不可靠, lua-弱表探測字串無效-字串是值不是物件-驗回收用堆積量測

## 知識

- [觀] titan C 版與 titan_dotnet 同構：Lua 全程拿不到 socket/fd/宿主物件。socket 鎖在 Gate 行程（C: titan_conn+libev，gate.c；C#: GateClient.Sock，Titan.Gate/GateApp.cs），Lua 宿主在 Proxy 行程；跨行程 node mesh 定址（C: titan_net pbc over TCP；C#: NetMQ TitanNode），節點身分 titan_net_id=char[8]（prefix2+ip4+port2）
- [觀] Lua 的連線證件=值型邏輯位址三件套：gate_id（titan_net_id cdata）+ client_uid/entity_uid（UUID 字串）。C# 物件若需給 Lua 持有一律 GCHandle.ToIntPtr 不透明 token（GooMem/GooHandles），Lua 只回傳不解參考
- [觀] 收包側（C#→Lua）=pull 模型：宿主每 tick 只呼一個無參數 Lua 函式 app_tick（FuncRefCall/titan_lua_func_ref_call），封包不逐包 pcall；資料塞具名 chan queue（GooChan/titan_chan），元素為原生 struct rpc{uid[37], buffer*, len}，Lua 端 goo.cast+goo.string 拉出後自行 protobuf unpack（rpc.lua server/client_unpack），拉完 elm.done() 釋放。chan 佇列只存在於此向
- [觀] 送包側（Lua→C#）=白名單 goo 符號直呼，無佇列：goo_rpc_s2s_send(net_id, uid, buf, len)／goo_rpc_s2c_send(gate_id, uuid2*, buf, len)／goo_gate_*_send 家族；宿主據 net_id 路由到目標節點，Gate 用 client_uid 查連線寫 socket。本機目標走 local_rpc_queue loopback 不過網路
- [觀] RPC=fire-and-forget 具名訊息（crc32("etype.func") 為索引，defs 由 JSON 載入），無 session id 配對、無 coroutine 掛起；回覆=反方向再發一次 RPC（entities[uid]:_on_rpc → self[func_name](args)）。s2s 收包甚至不帶來源 net_id，回覆位址從 AppData 分散式表（uid→{app_id,type_id,gate_id}）重查
- [觀] 非同步結果（DB/account/entity 生命週期）另走 handle 狀態機＋callback+timeout 佇列（goo_*_handle_new/_pull/_result 家族，同為 pull 模型），與網路 RPC 是兩套系統勿混淆
- [觀] tslg-servercore-lua（orbit）對映：ServerBase/ServiceBase/ClientBase 不外露給 Lua；等價做法=C# 維護 id→ClientBase 註冊表＋熱路徑開 goo 槽（SOP B）／控制面走 dotnet.call（SOP C）；收包側（C#→Lua）沿 V_FixedUpdate（=tick 執行緒，天然滿足 lua_State 執行緒親和鐵則）派發或 chan pull。現況 6 槽無任何網路符號
- [觀] 詞彙陷阱：「上行/下行」兩套慣例相反——LuaBridge_Cookbook 以呼叫方向定義（腳本=上層用戶：上行=C#→Lua 宿主驅動腳本、下行=Lua→C# 腳本要服務）；資料流直覺（腳本當終端：上行=送出/upload、下行=收入/download）則相反。溝通一律用箭頭（C#→Lua／Lua→C#）或「收包側/送包側」，勿裸用上行下行
- [觀] tslg-servercore-lua dev/lua+gate 已落地 titan 拓撲同構的 GateServer（Titan.Gate/GateServer.cs，ServerBase<GateClient>）：client socket 在 Gate 行程，後端 Account/Map 走 GateAgent（AgentBase/OneShot）池＋靜態組態＋FNV-1a hash 釘定（取代 titan node mesh+coord）；證件 ClientUid=gc{serial}（_clientTable）、EntityUid=CharacterId 字串（_entityTable，Map 下行 Push 反查寫 socket）；跨行程 Attach/Detach 取代同行程 MigrateFrom，未註冊 opcode 原樣 ForwardPack 雙向不透明轉發。Map 端本 repo 只有測試 fake（GateServerTest），真 Map=舊TSLG MapServer 待接
- [觀] TitanApp（--app gate，鏡射 app.c 五服務共用 main，現階段只做 gate）把 Lua 開在 Gate 行程（_enableLua）——與 titan 相反（titan gate 無 Lua，proxy 才有）。goo 送包槽落點依 Lua 最終住哪裁定：住 Map=goo_push(entity_uid) 經 Gate 回 client（titan goo_rpc_s2c_send 同款）；住 Gate=直查 _entityTable/_clientTable SendPacket（同行程，註冊表現成）
- [觀] Wells 裁定方向：Lua 落點=Map 端（遊戲邏輯側，titan Proxy 同位），角色只管邏輯不碰 I/O；Map 端玩家=代理 ClientBase（虛擬連線，真 socket 在 Gate，保 Orbit handler/module 生態不變）；收包走原 ServerBase 佇列→handler 彙整後 per-packet push 進 Lua（FuncRefCall 帶參變體，需新建），送包 Lua→goo 宿主方法→ClientBase.SendPacket 原路回
- [觀] titan chan 非額外層，就是 Orbit recv 佇列（_recvClientList/_recvQueue + V_FixedUpdate 排乾）的同位角色：都坐在「I/O 到達→tick 邏輯消費」之間，同一訊息只過一條佇列一次；「好幾個 chan」是每訊息域一條平行分流（struct 型別/消費者不同，C 端免 tagged-union）非串聯多層。titan 選 pull 因宿主是薄管道（路由全在 Lua，需整包過界）+1 pcall/tick+ffi≈0+零序列化經濟學；Orbit 宿主胖（派發/模組在 C#）→per-packet push 自然，chan 不必要，單 opcode 過熱再局部批次化；不變鐵則=Lua handler 不阻塞，慢操作非同步回拋
- [觀] 通用 TitanApp 定型（Wells 意向）：TitanApp(MainAppBase) 當 app.c 同位的通用殼，--app 選人格（gate/proxy/account/log/coord），每人格=XXXBase 組合（gate=ServerBase、map/proxy=ServiceBase<GateSlave> 接 Gate 連線）；Lua 基座（LuaRuntime+goo+dotnet.call+具名進入點）人格無關共用
- [觀] XXXBase 取代 chan 成立：chan 三職責對應 Orbit 現貨——跨執行緒交接=Base recv 佇列（handler 於 tick 執行緒跑）；節流背壓=per-frame cap/queue threshold；域分流=opcode handler。非網路域（DB/async 完成）回 tick 執行緒=InvokeDelegate/AppSyncContext（僅 MainAppBase）。取代不掉的只有 Lua 消費端 ABI：chan=pull、Base=push，代價=scripts 消費縫改寫（entities.lua _tick_* 拉取迴圈→具名進入點 on_rpc/on_gate_login/on_detach），保住解碼一次在Lua+ptr/len 零拷貝，放棄批次攝提（三性質中最便宜項）；需 pull/verbatim 時 chan 薄皮可逐域補掛（同執行緒免鎖）非單行道
- [觀] Wells 裁定：建 Node 類（titan_net/TitanNode 的 Orbit 對應物，跨服務鏈路層）取代裸用 ServiceBase——動機非刪重量而是把 titan node 概念（對等節點/定址/join-leave）帶進 Orbit 語彙；實作路徑三層：①包裝現貨（Node 持 ServiceBase<NodeSlave> 收側 + AgentBase 池發側 + peer 註冊表，零 fork）→②缺鉤子時原類加最小 virtual/event→③真頂牆才 fork ServiceCore 小鏈。Scope 圍欄：transport/定址/req-reply/push/鏈路生命週期，不含 Lua 派發與 entity。分期：P1 靜態組態（Gate 現況同款）、P2 GateServer 手工 agent 池遷入 Node、P3 coord/discovery 後補。命名建議 TitanNode（與 titan_dotnet 同名）避免裸 Node 撞容器語彙
- [觀] Node 類實作路徑改裁（Wells 最終裁定，取代先前「包裝現貨」建議）：參考 ServiceBase/SlaveBase 搬遷需要的功能成自足新類，不直接引用 Service 層；底盤仍沿用 ServerCore/ClientCore（app 主迴圈整合）。不搬：MetadataParser 握手（join 改走一般封包 NodeOpcode.Join，titan CMD_JOIN 同款）、HandlerHelper 反射糖（Node 層手寫 switch dispatch）、IMigratable。搬遷順手補：每幀消費節流（ServiceBase pump 原本無上限）。驗證錨：對端用現役 GateAgent 證協議相容（NetOneshot 語意照搬才成立）
- [觀] 分層修正（Wells 裁定）：Map=遺戲應用端不進 servercore；framework 側建 Titan.Proxy（ProxyNode : NodeBase<ProxyPeer>，business-blind Lua 宿主，titan TitanProxy 同位）：Attach→on_login、Forward→on_rpc、goo_send→Push，框架管到「封包進出 Lua 合約」為止；遺戲（Map）=日後部署在 Proxy 上的 entities/業務腳本+defs。TitanApp _knownApps 加 proxy，LaunchLua 從 gate 人格歸位（gate 腳手架退役）。⚠ 2026-07-16 首次實作（49fcb89）經 Wells 審後裁定「不是想像的樣子」已整組 reset 退回 c7faafa，方向待重裁；舊實作存 backup/proxy-goo-trim-5e91c94 分支備查
- [觀] E2E 測試缺口補法兩級：L1 整合測試（xunit）=GateServerTest 假 MapSvc 換真 Lua 宿主（echo 測試腳本充遺戲），raw TcpClient 走登入→Attach（含 Node Join）→Forward→Lua→Push 全鏈，原 15 案照綠；L2 行程級 smoke（腳本）=真起兩顆 Titan.App（--app gate/--app proxy）驗組態/部署面。PbGateMap 合約現居 Titan.Gate/Message，日後升共用專案解耦。注：xunit 下真 Lua 宿主必須全同步測試（async/await 續接跳執行緒會踩 lua_State 親和鐵則）＋組件停平行（49fcb89 實證過的手法，存 backup 分支）

## 行動

- Orbit 導入 Lua RPC 時：先決定連線證件形態（session id 整數 or uuid），建 C# 註冊表，再照 LuaBridge_Cookbook SOP B 開 goo_send 槽；收包側（C#→Lua）封包派發選 chan pull（titan 式）或 handler 內 FuncRefCall（orbit 現有設施），量大選前者
- 查 titan 實碼錨點：titan_dotnet scripts/core/entities.lua:98-169(cdef)/1755-1998(收包側)/2352-2434(送包側)、src/Titan.Lua/Goo/GooHost.cs:419-598、native/titangoo/titangoo.c:446-460；C 版 src/app/proxy/proxy.c:2676-3328、scripts/core/entities.lua 同構
- 碰 Proxy 實作前先與 Wells 對齊「他想像的樣子」：49fcb89 版（backup/proxy-goo-trim-5e91c94）被退的具體不滿未記錄，勿直接重施舊設計
