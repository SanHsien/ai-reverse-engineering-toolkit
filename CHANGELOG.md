[English](CHANGELOG.en.md) | 中文版

# 變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，新的在上面。

## 2026-10-26

### 修正

- `env_check.py`：相依工具有 `min_version` 但讀不出版本（命令逾時、輸出沒數字）時原本判為符合並放行 `--require` 閘門；改為 `unknown`（未就緒，顯示 `version unreadable`）。`--require` 指到只能手動確認的工具（`ghidramcp` 等）原本永遠回 1 且訊息誤導；改為結束碼 2 並說明。決策理由見 [docs/DECISIONS.md](docs/DECISIONS.md)。

- `ledger.py validate`：`evidence[].kind` 是清單或物件時丟出 `TypeError`（不是驗證錯誤）；改成回報 `evidence[j].kind` 錯誤。追溯到 Seen 改用不動點迭代：3000 層推論鏈不再 `RecursionError`，菱形依賴的梯子不再指數級卡住。
- `ledger.py render`：證據 `ref` 內含反引號會截斷行內程式碼，改用較長的分隔符；標題、主張、推理等欄位內的換行會開出假標題或項目，改折成單行。`-o` 寫不進去（目錄不存在等）原本是 traceback 且結束碼 1（與「有錯」混淆），改為訊息加結束碼 2。
- `tools/check_links.py`：非 ASCII 檔名（`git ls-files` 預設加引號跳脫）會讓檢查器找不到檔而當掉，改用 `-z`；已追蹤但工作樹已刪的檔不再當掉；`<含空白的路徑>` 與含成對括號的連結目標能正確解析；程式碼區塊與行內程式碼裡的範例連結不再誤報。

## 2026-10-24

### 修正

- `tools/dev_check.ps1`：`-BaseRef` 指向已不存在的 commit（例如 force-push 後的 `github.event.before`）時會略過該檢查，但殘留的 `$LASTEXITCODE` 讓腳本以非零結束、CI Windows gate 變紅；改為全部通過後明確 `exit 0`。

### 維護

- CI 的 Actions 釘選到 commit SHA 並升到 `actions/checkout` v7.0.1、`actions/setup-python` v7.1.0（v4／v5 為已淘汰的 Node 20），checkout 關閉 `persist-credentials`。
- 新增 `.github/dependabot.yml`（每週更新 GitHub Actions）與 CodeQL 工作流程（Python、Actions）。

## 2026-10-19

### 新增

- `ledger.py validate` 新增 `--json`：把檢查結果輸出成結構化 JSON（通過時含 `scope`、`findings` 數與各層級計數；不通過時含 `errors` 清單），與 `env_check.py --json` 一致，結束碼不變。
- `toolkit.json` 與 `ledger.py` 擴充合法依據：新增 `competitive-research`（競品黑箱架構調研）與 `legacy-modernization`（無原始碼老舊系統維護與遷移）。

### 變更

- 還原專案核心定位與技術深度：重新將 REA 技術架構、跨形態分析（Web/Electron IPC、Android ADB/JADX、原生二進位 Call Graph）、SaaS 護城河探討、資安防守方零信任 Client 假定與 7 大實戰落地方向整合至中英文 README 主體，破除自我設限。
- 移除過度審查之 `ComplianceTextTests`，並將 `AGENTS.md` 規則回歸使用者開發意志與不可妥協之硬閘門。

## 2026-10-16（工具化）

### 新增

- `env_check.py` 與 `toolkit.json`：檢查 10 個逆向分析工具的安裝狀態、版本與依賴（JDK、Node、.NET），缺的給安裝指令；可依用途篩選、`--require` 當閘門、`--json` 輸出。
- `ledger.py`：證據帳本檢查與轉 Markdown。強制宣告合法依據；Seen 需可重現證據；Inferred 需追溯到 Seen 且不得建立在 Unknown 上；Unknown 需寫下一步。
- `templates/agent-prompt.md`、`templates/ledger.example.json`。
- 測試（stdlib `unittest`，20 個，含合規字眼檢查）、`tools/dev_check.ps1`、GitHub Actions（Windows＋Ubuntu Python 3.10／3.13）。
- 雙語 README、MIT 授權、`.gitattributes`、`.editorconfig`。

### 修正

- `ledger.py`：`scope.basis` 或 `based_on` 不是字串時回報驗證錯誤，不再 TypeError；帳本不是 UTF-8 時結束碼 2。

### 變更

- 原 README 搬到 `docs/background-notes.md`，開頭標明是閱讀筆記；工具表移進新 README 與 `toolkit.json`。
- 第四章第 6 點「反查前端簽章做非官方 SDK」改寫為「為自己擁有的系統補上 API 文件與用戶端」。（2026-10-19 已還原為原文，見該日「還原專案核心定位與技術深度」。）
- 第四章第 3 點「競品黑箱架構調研」改寫為「用公開資料做架構研究（不拆解他人軟體）」；第 4、7 點補上授權與資料所有權條件。

## 2026-10-16（初版）

- 10 個 AI 逆向分析工具的整理、REA 技術分析、純淨室流程與合規聲明。
