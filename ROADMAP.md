# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `5768436d4b04` 查的快照，開工前先重查 GitHub。

## 現況

合法逆向分析的工具環境檢查（`env_check.py`、`toolkit.json`）與 Seen／Inferred／Unknown 證據帳本（`ledger.py`），自有 repo（public，非 fork，沒有上游）。健康：`CI`、`CodeQL`、`Dependency freshness` 預設分支最近一次皆 success（2026-10-28）；open issue 0 筆、open PR 0 筆；Dependabot 與 Code scanning 告警 0 筆；無 release。只用 Python 標準庫，沒有依賴宣告，唯一被比對的依賴是 workflow 釘住的 Actions。沒有卡住的事。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 無 | 深掃與新鮮度補強都已完成並推送，工作樹乾淨、無告警、無 open PR/issue；剩下的疑點目前沒有觸發使用情境，列在「中期」 | — | — | 2026-10-29 證據快照；接續開發報告（2026-10-25）、深掃報告（2026-10-26）、依賴新鮮度報告（2026-10-28） |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 擴充 `tools/check_links.py` 的連結語法 | repo 文件開始使用參考式連結（`[x]: path`）、`<a href>`、括號 title `[a](x.md (T))` 或含空白的目標 | 先寫測試（缺檔的該類連結修前不報、修後報；現有文件仍 0 錯誤）；`python tools/check_links.py` 與 `python -m unittest discover -s tests` 綠 | Claude Haiku | `tools/check_links.py`；深掃報告（2026-10-26）審查員列為後續 |
| 更新 `toolkit.json` 的工具條目 | 條目中的某個工具 repo 改名、下架、最低版本需求改變，或維護者要新增工具 | 條目的 `detect`／`requires`／`install` 與該工具官方文件一致；`python env_check.py --json` exit 0；`python -m unittest discover -s tests` 綠 | Claude Sonnet | `toolkit.json`；`env_check.py` |
| 處理新鮮度檢查的警示 | `Dependency freshness`（每月 1 日）轉紅，通常因 workflow 釘住的 Action 有新版 | 依 `tools/check_dependency_freshness.py` 的輸出升級釘選 SHA（對應 tag）或寫 deferral（帶 `revisit`）；該 workflow 綠、`ci.yml` 綠 | Codex | `.github/workflows/dependency-freshness.yml:12`；`docs/DECISIONS.md`（2026-10-28 條目）；依賴新鮮度報告（2026-10-28） |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 把 CI 的 `python-version`（3.10、3.13）納入新鮮度比對 | 那是支援範圍的承諾，不是依賴下限；決定記在 `docs/DECISIONS.md` | 調整支援的 Python 範圍時 |
| 加入第三方 pip／npm 依賴 | 工具刻意只用標準庫，`tomllib` 僅在讀 TOML 時延遲載入；新增依賴會同時改變新鮮度檢查的 `ECOSYSTEMS` 與 Dependabot 設定 | 標準庫無法達成某項必要功能時，且需同步更新新鮮度檢查與 Dependabot |
| 讓 `env_check.py --require` 接受手動偵測工具（如 ghidramcp） | 已決定改為用法錯誤（exit 2），因為手動工具無法自動判定就緒 | 該類工具有可程式化的偵測方式時 |

## 維護方式

自有 repo：以 `pwsh -NoProfile -File tools\dev_check.ps1` 與 `python -m unittest discover -s tests` 全綠為閘門；每月 `Dependency freshness`、每週 `CodeQL`、Dependabot 更新 Actions；有使用者可見變更才升版並建立 release。
