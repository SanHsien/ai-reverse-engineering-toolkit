[English](CHANGELOG.en.md) | 中文版

# 變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，新的在上面。

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
