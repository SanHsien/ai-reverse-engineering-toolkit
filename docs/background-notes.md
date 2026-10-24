# AI 輔助逆向分析的工具、架構與技術深度指南

> 整理自 Threads [@0xalpha.ai](https://www.threads.com/@0xalpha.ai/post/DecdMHQE_sj) 的「10 個讓 AI Agent 分析閉源軟體的 GitHub Repo」，並整合社群 [@aistart_up](https://www.threads.com/@aistart_up) 等對 REA (Reverse Engineer Anything) 的技術真相勘誤、SaaS 護城河探討、資安防守方轉變與工程落地架構。


---

## 一、 核心概念與架構圖

傳統逆向工程高度依賴人工在 GUI 介面中反覆尋找符號、單步除錯。本工具箱的核心精神是：**利用 MCP (Model Context Protocol)、CLI 介面與結構化 Skill SOP，讓 AI Agent 具備自主調用反編譯、流量抓取與動態插樁的能力**，並由 Agent 產出規格文件、資料遷移腳本或相容層（對象限 README〈使用範圍〉列出的情境）。

```
                     ┌───────────────────────────────┐
                     │    AI Agent (大腦 / 決策)      │
                     └──────────────┬────────────────┘
                                    │ (MCP / CLI / Skill)
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
   【網路與協議分析】            【靜態二進位 / 代碼】         【動態執行期插樁】
    - mitmproxy                 - Ghidra / GhidraMCP        - Frida
                                - ImHex (Hex + MCP)
                                - ILSpy (.NET / C#)
                                - Cpp2IL (Unity 遊戲)
                                - Android RE Skill (APK)
                                - Universal Modder (遊戲)
         │                          │                          │
         └──────────────────────────┴──────────────────────────┘
                                    │
                                    ▼
                     【總協調入口：REA (morluto/rea)】
                     單一 MCP 入口串聯多種分析引擎
```

---

## 二、 10 個核心 GitHub Repo

工具清單、安裝方式與適用範圍已整理進 [README](../README.md#工具清單) 與 `toolkit.json`。

---

## 三、 REA (Reverse Engineer Anything) 深度技術真相與勘誤

隨著社群熱議，許多關於 REA 的傳言需要理性釐清其架構真相、跨形態能力與法律邊界：

### 1. REA 的架構本質（勘誤）
- **本身不含反編譯器**：REA 不是自己從頭寫一個神奇的反編譯引擎，它本質是 **MCP Server 工具鏈膠水**，將本地端現有的老牌逆向工具整合包裝，轉譯給 Claude Code、Codex 等 AI Agent 調用。
- **重度依賴本地工具環境**：
  - Windows/Linux 原生二進位：本機需預先配置 Ghidra、Hopper 或 IDA Pro。
  - Android APK：依賴 JADX 及完整 JDK。
  - 韌體/二進位解包：需 Linux 環境與 Binwalk / Unblob。
- **真正的創新點在於「證據帳本 (Reconstruction Ledger)」**：
  - 傳統 LLM 逆向容易產生幻覺（憑空捏造符合語意的偽代碼）。
  - REA 強制結構化輸出：明確標註「在哪個十六進位偏移量找到」、「關聯的調用引用」、「推論與未驗證邊界」，大幅降低 Agent 瞎猜機率。

### 2. 跨形態的深度分析能力（不限於傳統 C/C++ 二進位）
- **Web 與 Electron 桌面應用**：
  - 自動拆解前端打包後的 JS 模組（Webpack/Vite chunks）、前端路由與混淆邏輯。
  - 萃取 Electron 桌面應用的 **IPC 通道（Inter-Process Communication）通訊邏輯**與本機橋接。
  - 自動追蹤/重構應用程式與後端之間的 API 呼叫、封包結構與請求合約。
- **Android APK**：
  - 整合 Headless JADX 自動萃取 Class 結構與邏輯。
  - 支援串接 **ADB** 搭配真機或模擬器觸發 UI 事件，動態對應函數調用路徑。
- **原生二進位 (.exe / .so / .dylib)**：
  - 透過 Ghidra/IDA/Hopper 萃取字串表、符號表，自動繪製 Function Call Graph（呼叫關係圖）。

### 3. 關鍵案例澄清與法律風險
- **ArtCraft 案例澄清**：社群曾誤傳「以 Rust 開發的 Adobe 免費開源替代品 ArtCraft」是由 REA 逆向生成。作者 Brandon Thomas 已公開澄清**完全沒有使用 REA**；甚至為避免智慧財產權侵權訴訟，其團隊嚴格禁止使用 Ghidra 等逆向工具，完全遵循只閱讀公開格式標準與規格文件的**純淨室設計（Clean-Room Design）**。
- **法律邊界（EULA 與乾淨室）**：
  - 商業軟體多數具有反逆向工程之 EULA 條款。
  - 將二進位檔直接餵給單一 Agent 重寫，依然存在重現專有邏輯/版權代碼的法律灰區。
  - 合規的作法必須落實「雙盲純淨室」：規格提取人員與編碼實作人員完全隔離。

### 4. 對 SaaS 護城河與資安防守方的典範轉移
- **純功能 Commodity 化（商品化）**：
  - 純業務邏輯與介面實作在 Agent 時代將不再是不可逾越的護城河。
  - 商業價值將如同昔日 Napster 對音樂產業的衝擊一樣，由「販售軟體二進位」轉移為「販售即時運算體驗、資料黏著度、通路與服務生態」。
- **未來軟體的真正護城河**：
  1. **專有資料與上下文積累**（使用者歷程、私有資料資產）。
  2. **工作流嵌入度 (Workflow Lock-in)** 與跨系統整合度。
  3. **分發通路與網路效應**。
  4. **品牌信任度與合規保障**。
- **資安防守方的全新假定**：
  - **程式碼混淆（Obfuscation）效益劇降**：過去能拖延人類專家數週的控制流平坦化、符號混淆，在長上下文推理 Agent 面前幾乎失去防護價值。
  - **零信任 Client 假定（Zero-Trust Client）**：前端、桌面客戶端、二進位預設「無秘密」；商業核心演算法與資安敏感邏輯必須強制收斂至**後端伺服器（Server-side）**，不可再依賴 client 端的混淆保護。

---

## 四、 可以仿照落地的 7 大實戰方向

### 1. 落地「證據鏈驅動」的 Agent 回報規範 (Reconstruction Ledger)
* **做法**：在團隊的 Agent Prompt 或驗證協定中，強制要求結論分層標記：
  * `[Seen/Verified]`：有實際執行檢查日誌、確切行號或十六進位偏移量。
  * `[Inferred/Guessed]`：模型根據命名或模式推導出的假設。
  * `[Unknown/Gap]`：尚未覆蓋或當前環境無法驗證的邊界。

### 2. 打造安全合規的「純淨室重構」雙代理工作流 (Clean-Room Workflow)
* **做法**：
  * **Phase 1（規格/分析 Agent）**：分析目標行為，僅產出 API 規格書、狀態機圖表與邊界合約（不含任何專有代碼）。
  * **Phase 2（實作 Agent）**：完全隔離於原始檔案之外，純粹依據 Phase 1 的合約規範重寫測試案例與實現代碼。

### 3. 競品黑箱架構調研（Competitive Architecture Research）
* **做法**：分析競品優秀功能（如離線資料庫同步機制、本地快取策略、特殊排版演算法）的底層設計，讓 Agent 提取「架構與行為規格書」供自研產品參考。

### 4. 無原始碼 Legacy 老舊系統維護與現代化遷移
* **做法**：針對企業內部遺失原始碼的舊 DLL、工具或驅動，讓 Agent 透過反編譯理解業務邏輯與介面合約，產出現代化（如 C# / Rust / Go）的重構替代版本。

### 5. 打造私有工具的 MCP 封裝（仿照 REA 思維）
* **做法**：不要試圖重造輪子，而是將團隊現有的各類命令列工具、日報收割腳本或資料庫管理指令封裝成標準 MCP Tool，讓 Agent 能即插即用。

### 6. 打造自用「未公開 API SDK」或系統相容層
* **做法**：
  1. 使用 **mitmproxy** 錄製通訊封包。
  2. Agent 解析 Header 認證規則與 Payload 格式。
  3. 若前端有簽章加密，以 **ILSpy** (.NET) 或 **REA** (Electron) 反查簽章演算法。
  4. 讓 Agent 自動生成 Python / TypeScript 版的非官方 SDK。

### 7. 專屬私有檔案格式救援與資料移轉 (Data Migration)
* **做法**：
  1. 利用 **ImHex** Pattern Language 切出二進位結構區塊。
  2. Agent 讀取結構切片，產出解析器代碼。
  3. 若含簡單加密，以 **Ghidra / REA** 提取解密邏輯，批量轉出 JSON/CSV。

---

## 五、 相關影音深入參考
- [YouTube: 為什麼整個 GitHub 都在瘋傳 REA？](https://www.youtube.com/watch?v=nmzKH9t4Zos)
- [YouTube: 5 分鐘看懂 Reverse Engineer Anything](https://youtu.be/m4D0wr01DbA)

---

## 六、 合規與責任聲明
> 依據開源社群指引與軟體工程道德標準：本工具箱與逆向分析技術僅限用於**個人擁有之軟體、獲合法授權之測試評估、資安漏洞防禦、系統互操作性 (Interoperability) 與數位資產保存**。商用工具請自行取得合法授權。
