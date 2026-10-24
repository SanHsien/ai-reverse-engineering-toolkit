# 給 AI agent 的分析回報提示詞

把下面整段放進分析任務的提示詞，要求 agent 以證據帳本回報。產出的 JSON 用
`python ledger.py validate <檔案>` 檢查，通過後 `python ledger.py render <檔案> -o report.md` 轉成報告。

---

開始之前，先確認分析範圍：

- 對象是什麼、屬於誰
- 合法依據是以下哪一種：`own-software`（自己擁有或開發的軟體）、`authorized-test`（有書面授權的測試）、
  `interoperability`（法律允許範圍內的互通性）、`data-recovery`（救援自己擁有的資料）、`defense`（資安防禦）
- 為什麼可以分析它

以上任何一項說不清楚，就**停下來問我**，不要開始分析。對象屬於第三方且沒有授權時，不分析。

分析時遵守：

1. 不取出、不重製目標的原始碼或受保護內容到回報裡；只描述行為、格式與介面。
2. 不嘗試破解授權、繞過 DRM、防作弊或存取控制。
3. 只在本機與自己擁有的環境執行，不對第三方服務送出流量。

回報格式：一個 JSON 檔，結構如下。

```json
{
  "title": "一句話標題",
  "scope": {"target": "…", "basis": "data-recovery", "authorization": "…", "date": "YYYY-MM-DD"},
  "findings": [
    {"id": "F1", "level": "seen", "claim": "…", "evidence": [{"kind": "file-offset", "ref": "file@0x10", "note": "…"}]},
    {"id": "F2", "level": "inferred", "claim": "…", "based_on": ["F1"], "reasoning": "…", "confidence": "高／中／低：理由"},
    {"id": "F3", "level": "unknown", "claim": "…", "next_step": "…"}
  ]
}
```

分層規則：

- `seen`：你實際執行或看到的。每條都要有證據，`kind` 是 `file-offset`、`file-line`、`command`、`capture`、`screenshot` 之一，
  `ref` 寫到別人能重現的程度（偏移量、路徑:行號、完整指令）。
- `inferred`：從 seen 推出來的。寫明 `based_on` 與推理過程；推論不能建立在 unknown 上。
- `unknown`：還沒驗證或無法驗證的。寫 `next_step`。

寧可多寫 unknown，也不要把猜測寫成 seen。
