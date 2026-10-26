English | [中文版](README.md)

# AI Reverse Engineering Toolkit & Workflows

> Curated from Threads [@0xalpha.ai](https://www.threads.com/@0xalpha.ai/post/DecdMHQE_sj) ("10 GitHub Repos for AI Agents Analyzing Closed-Source Software"), combined with community technical analysis from [@aistart_up](https://www.threads.com/@aistart_up) on REA (Reverse Engineer Anything), SaaS moat impacts, zero-trust client defense, and engineering workflows.
> Provides an end-to-end AI reverse engineering solution: local toolchain diagnostic engine (`env_check.py`), structured reconstruction evidence ledger validator (`ledger.py`), agent prompts, and 7 production-grade implementation workflows.

---

## 1. Core Concept & Architecture

Traditional reverse engineering relies heavily on manual GUI inspection, stepping through disassemblers, and symbol hunting. This toolkit enables **AI Agents to autonomously orchestrate decompilation, traffic capture, and dynamic instrumentation via MCP (Model Context Protocol), CLI interfaces, and structured Skill SOPs**, producing formal API specifications, format migration scripts, and interoperability layers.

```
                     ┌───────────────────────────────┐
                     │    AI Agent (Brain / Policy)  │
                     └──────────────┬────────────────┘
                                    │ (MCP / CLI / Skill)
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
   【Network & Protocols】        【Static Binaries / Code】     【Dynamic Instrumentation】
    - mitmproxy                 - Ghidra / GhidraMCP        - Frida
                                - ImHex (Hex + MCP)
                                - ILSpy (.NET / C#)
                                - Cpp2IL (Unity IL2CPP)
                                - Android RE Skill (APK)
                                - Universal Modder (Game)
         │                          │                          │
         └──────────────────────────┴──────────────────────────┘
                                    │
                                    ▼
                     【Orchestrator: REA (morluto/rea)】
                     Unified MCP gateway connecting multiple engines
                                    │
                                    ▼
                     【Evidence Ledger: Reconstruction Ledger】
                     Enforcing Seen / Inferred / Unknown tiers against hallucinations
```

---

## 2. 10 Core Repositories & Tool Matrix

All 10 tools can be diagnosed automatically via `env_check.py`:

| # | Tool | Role & Key Highlights | Applicable Scope | Installation |
|---|---|---|---|---|
| 1 | [REA](https://github.com/morluto/rea) | **Unified MCP Orchestrator**: Bridges existing local tools to Claude Code / Codex agents. Innovated the Reconstruction Ledger against LLM hallucinations. | All | `npx rea-agents setup` (Node 22.19+) |
| 2 | [Ghidra](https://github.com/NationalSecurityAgency/ghidra) | **NSA Open Source Native Decompiler**: Full support for x86/ARM/MIPS, high-fidelity decompilation, Headless scriptable analysis. | own-software, interoperability, data-recovery, defense, legacy-modernization | Download GitHub Releases, set `GHIDRA_INSTALL_DIR` (JDK 21+) |
| 3 | [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) | **MCP Bridge for Ghidra**: Built by security researcher LaurieWired, lets agents query decompiled code and call graphs directly. | own-software, interoperability, defense, legacy-modernization | Ghidra extension |
| 4 | [ImHex](https://github.com/WerWolv/ImHex) | **Modern Hex Editor**: C-like Pattern Language for binary templates, custom format slicing, MCP integration. | own-software, data-recovery, defense, competitive-research | `winget install WerWolv.ImHex` |
| 5 | [mitmproxy](https://github.com/mitmproxy/mitmproxy) | **Interactive HTTPS Proxy**: Python-scriptable proxy to inspect, record, replay and map network protocols. | own-software, interoperability, defense, competitive-research | `pipx install mitmproxy` |
| 6 | [ILSpy](https://github.com/icsharpcode/ILSpy) | **.NET / C# Decompiler**: Cross-platform CLI (`ilspycmd`), high-fidelity CIL reconstruction to readable C#. | All | `dotnet tool install --global ilspycmd` |
| 7 | [Frida](https://github.com/frida/frida) | **Dynamic Instrumentation Toolkit**: Injects JS hooks into native processes to inspect memory, intercept keys, and verify static inferences. | own-software, defense, competitive-research | `pipx install frida-tools` |
| 8 | [Android RE Skill](https://github.com/SimoneAvogadro/android-reverse-engineering-skill) | **Android APK RE Workflow Skill**: Standardizes jadx and apktool analysis into executable Agent Skills. | own-software, defense, competitive-research | Per repo instructions (requires jadx, apktool) |
| 9 | [Universal Modder](https://github.com/rehan-remade/universal-modder) | **Game Modding Workflow Skill**: Agent workflows tailored for binary modding, asset injection, and architecture analysis. | own-software, interoperability | Per repo instructions |
| 10 | [Cpp2IL](https://github.com/SamboyCoding/Cpp2IL) | **Unity IL2CPP Restoration Bridge**: Restores Unity native C++ binaries back to .NET metadata for ILSpy analysis. | own-software, interoperability, data-recovery, legacy-modernization | Download standalone binary from GitHub Releases |

---

## 3. REA (Reverse Engineer Anything) Technical Truths

Clarifying REA architecture, cross-modal capabilities, and real-world boundaries:

### 1. Architectural Essence
- **MCP Glue, Not a New Decompiler Engine**: REA does not implement its own decompiler; it packages proven local tools into standard MCP endpoints for agents like Claude Code.
- **Local Toolchain Dependencies**: Requires local installations of Ghidra, JADX, JDK, or Binwalk.
- **Real Innovation: The Reconstruction Ledger**:
  - Unconstrained LLMs frequently hallucinate plausible-looking pseudo-code.
  - REA enforces a structured output contract: hex offsets, xref call citations, and explicit boundaries between verified facts and inferences.

### 2. Cross-Modal Depth (Beyond C/C++ Binaries)
- **Web & Electron Applications**:
  - De-bundles frontend modules (Webpack/Vite chunks), routes, and obfuscation.
  - Extracts Electron **IPC (Inter-Process Communication)** message handlers and native bridges.
  - Reconstructs internal API request contracts and schemas.
- **Android APKs**:
  - Headless JADX extraction of classes and lifecycle flows.
  - **ADB** connectivity with real devices/emulators to trigger UI events and map runtime tracepoints.
- **Native Binaries (.exe / .so / .dylib)**:
  - Extracts strings, export/import symbols via Ghidra/IDA, and renders function call graphs.

### 3. Clean-Room Design & Legal Boundaries
- **The ArtCraft Precedent**: Rumors that the open-source Adobe alternative "ArtCraft" was generated with REA were debunked. Creator Brandon Thomas confirmed no decompilers were used; his team adhered to a strict **Clean-Room Design** relying only on open standards and specifications.
- **Clean-Room Dual-Agent Protocol**: Strict separation between the specification extractor agent and the implementation coding agent protects against copyright infringement.

### 4. SaaS Moats & The Zero-Trust Client Paradigm Shift
- **Commoditization of Pure Logic**: UI and boilerplate logic cease to be defensible moats against agentic decompilation.
- **New True Moats**: Proprietary datasets, user workflow lock-in, distribution channels, and operational trust.
- **Zero-Trust Client Reality**:
  - Code obfuscation no longer creates meaningful defense against long-context reasoning agents.
  - All clients (Web, Electron, Mobile, Native) must be assumed transparent; core business algorithms and access controls must reside server-side.

---

## 4. 7 Actionable Implementation Workflows

### 1. Evidence Ledger Driven Reports (Reconstruction Ledger)
* Require agents to classify all findings into:
  * `[Seen/Verified]`: Explicit command logs, hex offsets, or exact file lines.
  * `[Inferred/Guessed]`: Hypotheses deduced from patterns or naming.
  * `[Unknown/Gap]`: Uncovered areas or limitations.
* Handled out-of-the-box by `ledger.py` and `templates/ledger.example.json`.

### 2. Clean-Room Dual-Agent Workflow
* **Phase 1 (Spec Agent)**: Extracts pure interface contracts, state machine specs, and behavioral schemas without proprietary code.
* **Phase 2 (Implementation Agent)**: Completely isolated from the binary, writing clean code and test suites purely from the Phase 1 specification.

### 3. Competitive Architecture Research
* Extract architecture specifications, offline synchronization patterns, caching strategies, or algorithmic models from closed-source products to inform internal designs.

### 4. Legacy System Maintenance & Modernization
* Recover missing business logic and interface contracts from orphaned DLLs and drivers to build modern replacements (e.g., C#, Rust, Go).

### 5. Custom Tool MCP Packaging (The REA Pattern)
* Wrap internal CLI tools, scrapers, or database utilities into standard MCP servers for instant agent reuse.

### 6. Unpublished API SDK & Compatibility Layers
1. Capture HTTP/HTTPS network traffic via **mitmproxy**.
2. Agent parses headers, authorization schemes, and payload structures.
3. If signatures are present, trace signature generation routines using **ILSpy** or **REA**.
4. Automatically synthesize Python or TypeScript SDKs and integration tests.

### 7. Proprietary File Format Rescue & Data Migration
1. Define structural slices with **ImHex** Pattern Language.
2. Agent reads structure slices and generates schema decoders.
3. Extract decryption routines via **Ghidra / REA** for bulk JSON/CSV migration.

---

## 5. Executable Toolchain

Two zero-dependency, pure Python standard library tools:

| Tool | Purpose | Features |
|---|---|---|
| `env_check.py` | Local Toolchain Diagnostics | Reads `toolkit.json`, checks tool availability and dependency versions (JDK, Node, .NET), supports `--use-case`, `--require`, `--json` |
| `ledger.py` | Evidence Ledger Validator & Renderer | Machine-checks evidence chains, level constraints, renders to Markdown, supports `--json` |

Includes [agent prompt template](templates/agent-prompt.md) and [example ledger](templates/ledger.example.json).

### Quick Start
```bash
# Check all 10 tools
python env_check.py

# Filter by use case
python env_check.py --use-case competitive-research

# Enforce required dependencies
python env_check.py --require ilspy,imhex

# JSON output for CI or Agents
python env_check.py --json

# Validate evidence ledger
python ledger.py validate templates/ledger.example.json
python ledger.py validate templates/ledger.example.json --json

# Render verified ledger to Markdown
python ledger.py render templates/ledger.example.json -o report.md
```

`--require` accepts only auto-detectable tools; ones that can only be confirmed by hand (`ghidramcp`, `android-re-skill`, `universal-modder`) exit with code 2. A dependency that has a minimum version but whose version cannot be read counts as not ready, never as passing.

### Ledger Rule Matrix

| Level | Definition | Required Fields |
|---|---|---|
| `seen` | Observed with reproducible evidence | `evidence` list with `kind` (`file-offset`, `file-line`, `command`, `capture`, `screenshot`) and `ref` |
| `inferred` | Deduced from verified facts | `based_on` (must trace to `seen`), `reasoning` |
| `unknown` | Unverified gaps | `next_step` |

Supported legal scopes (`scope.basis` in [`toolkit.json`](toolkit.json)):
- `own-software`: Internal software with lost source, debugging, auditing
- `authorized-test`: Formal written penetration tests
- `interoperability`: Lawful interoperability and format compatibility
- `data-recovery`: Rescuing proprietary data assets
- `defense`: Malware analysis and defensive posture validation
- `competitive-research`: Black-box competitive architecture extraction
- `legacy-modernization`: Decompilation and migration of orphaned systems

---

## 6. References & Media

- [YouTube: Why GitHub Went Crazy Over REA](https://www.youtube.com/watch?v=nmzKH9t4Zos)
- [YouTube: Reverse Engineer Anything Explained in 5 Minutes](https://youtu.be/m4D0wr01DbA)

---

## 7. Development & Verification

```bash
# Unit tests
python -m unittest discover -s tests -v

# Relative link integrity
python tools/check_links.py

# Windows canonical gate
pwsh -File tools/dev_check.ps1
```

Further notes in [`docs/background-notes.md`](docs/background-notes.md).

---

## 8. License

[MIT](LICENSE)
