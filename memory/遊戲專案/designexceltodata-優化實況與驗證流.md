# designexceltodata-優化實況與驗證流



- Scope: global

- Author: wellstseng

- Confidence: [觀]

- Trigger: DesignExcelToData, 產檔器, Design產檔器, CLI批次, CliRunner, 增量產出, EqualsWithoutHeader, FLAG_ForceGenOutput, GoldenMaster, GenReport, DataValidator, 驗證規則, SrcInfoMap, GenerateOneExcel, CliLastRun

- Created-at: 2026-07-03



## 知識



- [觀] Phase 0-2 完成實況（被 replace 覆蓋後補回）：Phase 0 GoldenMaster.ps1（snapshot/compare，baseline 為 bgm/sfx/voice 三表覆蓋；.bytes跳前4byte/.json正規化gtime/.cs .dat精確比）；Phase 1 GenReport收集器（批次期間 Util.Log 改道不彈窗、FormGenReport 一次總結）+ MainLogic.Generate.cs 編排下沉（GenerateOneExcel：Load→Verify→Write→GenScripts，UI/CLI共用）+ Util.ParseSheetNameFilter 抽出（順修FormMain:267 strSE[i]→[j] bug）；Phase 2 DataValidator（外部規則檔 ExcelToData設定檔/[checksum]_表單欄位驗證規則 fallback 預設_；範圍/集合/非空/唯一=Error擋該表，型別dry-run+重複ID=Warn，FLAG_WarnAsError升級）+ CExcelTableWorkingData.SrcInfoMap（id→來源檔+行，MergeTables會clone DataRow故以id為key）；驗證資產 RunGenHarness.ps1（反射產檔）/RunBadDataTest.ps1

- [觀] 2026-07-03 Phase 3（CLI批次+增量產出）完成並驗收全過：Program.Main(args) 分流（有參數→CliRunner.Run，不建介面、不回寫RuntimeData；無參數→現行UI）；CliRunner.cs 手寫參數解析+AttachConsole(-1)+CliLog(console+log檔雙輸出，預設 App資料/CliLastRun.log)；exit 0成功/1產檔錯誤/2致命

- [觀] CLI 旗標還原順序：UI介面預設值 → RuntimeData 勾選紀錄（MainLogic.TryGetSavedCheckBoxState）→ CLI 參數覆寫；文法 -all / -files a.xlsx;b.xls（相對src或絕對）/ -sheets(同UI含a-b範圍) / -src/-serout/-cliout / -force / -noscript / -linkcheck/-nolinkcheck / -strict(=DataValidator.FLAG_WarnAsError) / -log

- [觀] 增量產出：Util.EqualsWithoutHeader(移植SGI C:/TSG/Misc/ExcelToData Utility/Util.cs:622) + WriteAllBytesIfChanged(bytes跳前4byte)/WriteAllTextIfChanged(json經NormalizeJsonGtime歸零比對、.cs/.dat精確比)；hook 在 DataWrite_CliByte/DataWrite_SerJson/ScriptProcessing.cs:309,383/Avg.cs:36/DataProcessing.WriteTableData；MainLogic.FLAG_ForceGenOutput（UI checkbox「強制產出(不比對差異)」CBox_ForceGenOutput / CLI -force）跳過比對；GenReport.CountFile 記寫出/略過

- [觀] 已接受行為（勿當bug修）：跳寫時檔內保留舊TimeStamp/gtime（時間戳只在內容變動時前進，與SGI一致）；WinExe+AttachConsole console輸出與cmd提示符交錯，CI用 cmd /c + exit code + log檔為契約

- [觀] Phase 3 驗收實測：-all exit0；立即重跑 寫0略12全略過；-force 全重寫12檔 GoldenMaster compare 皆綠；壞資料 exit1 且log含 表/ID/檔案/行數/欄位/值 完整定位；錯參數與缺-all/-files exit2；UI啟閉回歸正常（RuntimeData正常回寫含新checkbox）；新增 _Verify/RunCliBadDataTest.ps1（CLI壞資料+錯參數驗收，可重跑）

- [觀] 驗收環境坑：本機沙箱 Design/Form 只有3個測試Excel（bgm/sfx/voice）；cmd傳中文exe名在CP65001下會失敗（sandbox環境連8.3短名也擋），PowerShell 用 `& .\Design產檔器.exe -all | Out-Null` 管線強制等待取$LASTEXITCODE；PS5.1跑無BOM UTF-8 .ps1 會以CP950誤讀中文路徑，_Verify腳本一律存UTF-8含BOM

- [觀] 下一階段 Phase 4（Server bytes+Server生成腳本）：ScriptProcessing參數化(namespace TSLG.Server.Design/去Il2Cpp attribute/欄位集serverHeadMap)、client呼叫路徑輸出逐字不變(golden master驗證)、輸出到 server路徑/dat/ 與 /scripts/、UI checkbox+CLI -serverbytes/-noserverbytes、GoldenMaster baseline擴充
- [觀] 2026-07-03 Phase 4（最終期）完成：Server bytes + Server 生成腳本，全計畫（Phase 0-4）收官。純新增輸出、預設關閉，開關 UI「產Server bytes+腳本」checkbox / CLI -serverbytes|-noserverbytes → MainLogic.FLAG_GenServerBytes
- [觀] ScriptProcessing 參數化 RScriptGenOpt{Namespace, WithUnity, OutRootDir}：client 呼叫路徑帶現值（TSLG.Hotfix.Design/WithUnity/GetScriptDesignRootDir）生成 .cs 逐字不變；server 版去 Unity 化（無 Il2Cpp/UnityEngine、錯誤 log 改 System.Console.WriteLine）、namespace 預設 TSLG.Server.Design（設定檔 ExcelToData設定檔/Server腳本namespace.txt 可改）
- [觀] Server bytes：MainLogic.DataWrite_SerByte → <SER路徑>/dat/*.bytes，餵既有 GenDataToBytes + server 欄位集（TableToDataDefMap(C_OUT_TAR_SERVER, IsMultiMerge)——多檔合併比照 client 排序，與 server 腳本欄位順序一致），與 client bytes 共用同一 TimeStamp；server 腳本掛在 GenAllWorkingScripts（置於 client 早退 return 之前），輸出 <SER路徑>/scripts/auto_generate/ + server 版 DesignData.Form.AutoGen.cs；CLI -noscript 會連 server 腳本一起關
- [觀] Phase 4 驗收工具：_Verify/RunServerBytesTest.ps1（合成 sc/s/c 混合欄位 xls → 驗 (b)bytes 依 server 腳本欄位順序逐值解析=json、欄位集相等、共用 timestamp、增量略過、(c)關閉零輸出；client 腳本輸出以 設定檔/腳本輸出根目錄.txt 暫時重導避免污染 golden）；_Verify/RunServerScriptCompile.ps1（server 腳本搭 Titan 等價 stub .NET 8 編譯 0錯0警）。Titan 端需自備 BinaryUtil/Defines.BytesString/IDesignForm/IDesignRow/DesignAttribute/各表 OnParsed partial
- [觀] 踩坑：真實 exe 跑測試表會把 test_*.dat 漏進共用 CheckBin（DataProcessing.WriteTableData 固定寫 exe 目錄下、不受 -serout/-cliout 影響）→ 測試腳本 finally 需清理，否則污染 GoldenMaster baseline；反射 harness 不會漏（GetAppFileName=powershell → 另一個 BIN 目錄）
- [觀] 沙箱三表 bgm/sfx/voice 為 client-only（無 s 欄位）→ 真實 fixture 產不出 server 輸出，S 目錄恆空；GoldenMaster Ser 目標本來就遞迴掃描，dat/ 與 scripts/ 無需另列目標即自動納入 baseline

## 行動



- 改CLI行為 → Tools/DesignExcelToData/ExcelToData/AppCodes/CliRunner.cs；改增量比對 → Util.cs 增量產出 region；驗收 → _Verify/GoldenMaster.ps1 compare + RunCliBadDataTest.ps1

- 每Phase收尾：msbuild Release + GoldenMaster compare 全綠才算過；文件同步 _AIDocs/DesignExcelTool_Source.md §9（批次優化層總覽）

