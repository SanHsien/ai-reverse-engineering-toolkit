# 決策紀錄

新的在上面。

## 2026-10-28 依賴新鮮度：只比對 workflow 釘住的 Actions

1. **為什麼要加。** 艦隊稽核的 `fre` 欄是紅的，原因是本 repo 沒有新鮮度檢查，不是某個依賴過期。Dependabot 只會一次開一個升級 PR，回答不了「宣告的版本整體落後多少」。
2. **比對什麼。** 本工具只用 Python 標準庫（`git grep` 所有 import 都是標準庫），沒有 requirements 檔或 pyproject，所以 `ECOSYSTEMS` 是空的，只比對 `.github/workflows/*.yml` 的 `uses:` 釘版。CI 的 `python-version`（3.10、3.13）不在比對範圍：那是支援範圍的承諾，由矩陣本身測。
3. **首次結果（2026-10-28）。** `actions/checkout` v7.0.1、`actions/setup-python` v7.1.0、`github/codeql-action/init`／`analyze` v4.39.1，全部是最新版，不需要升級，也沒有 hold 或 deferral。
4. **紅燈的出口。** 宣告行加 `# freshness-hold: <理由>`（常態政策），或在 `.github/dependency-deferrals.json` 寫 `deferredLatest`＋`reason`（這個月不升，上游超過那版會自動再問）。提高宣告版本只為了讓報告變綠不是出口。
5. **腳本來源。** 從 `agent-session-restore` 的通用版複製，只改 `USER_AGENT`、`ECOSYSTEMS` 與註解；`ECOSYSTEMS` 改回 `("pypi",)` 時合約測試 `test_every_checked_ecosystem_is_also_watched_by_dependabot` 會失敗（已做突變驗證）。

## 2026-10-26 env_check 的 `--require` 閘門

1. **讀不出版本不放行。** `--require` 是 CI 或 Agent 用來擋「環境不合格」的閘門；有版本下限卻讀不出版本時，無法證明符合，放行就等於閘門失效。改為 `unknown`（未就緒、`--require` 回 1）。代價：命令逾時或輸出格式怪異的環境會被擋，使用者需自行確認版本；沒有版本下限的相依（如 .NET SDK）不受影響。
2. **手動確認的工具不能被 `--require`。** `detect.manual` 的工具（`ghidramcp`、`android-re-skill`、`universal-modder`）本機偵測不到，原本永遠回 1 且訊息只說「not ready」。改為用法錯誤（結束碼 2）並列出哪些 id 不可用，讓呼叫端立刻知道是參數問題而不是環境問題。
3. 不採用的做法：把手動工具直接從 `--require` 靜默排除（會讓呼叫端以為已檢查）。
