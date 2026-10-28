English | [中文版](CHANGELOG.md)

# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), newest first.

## 2026-10-28

### Added

- Dependency freshness check: `tools/check_dependency_freshness.py` (the fleet's generic version), a monthly `.github/workflows/dependency-freshness.yml`, `.github/dependency-deferrals.json`, and contract tests in `tests/test_dependency_freshness.py`. The toolkit uses the standard library only, so its declared dependencies are the GitHub Actions pinned in the workflows; on the first run all four are at their latest release. Rationale in [docs/DECISIONS.md](docs/DECISIONS.md).

## 2026-10-26

### Fixed

- `env_check.py`: a dependency with `min_version` whose version could not be read (timeout, no digits in output) used to count as satisfied and pass the `--require` gate; it is now `unknown` (not ready, shown as `version unreadable`). `--require` on a hand-check-only tool (`ghidramcp`, etc.) always exited 1 with a misleading message; it now exits 2 with an explanation. Rationale in [docs/DECISIONS.md](docs/DECISIONS.md).

- `ledger.py validate`: a list or object in `evidence[].kind` raised `TypeError` instead of a validation error; it now reports the `evidence[j].kind` error. Tracing to Seen is now an iterative fixpoint: a 3000-link inference chain no longer hits `RecursionError`, and a diamond-shaped ladder no longer blows up exponentially.
- `ledger.py render`: backticks in an evidence `ref` cut the inline code short (now uses a longer delimiter); newlines in title, claim, reasoning and similar fields could open fake headings or bullets (now folded to one line). An unwritable `-o` target (missing directory, etc.) produced a traceback with exit 1, which collides with "ledger has errors"; it now prints a message and exits 2.
- `tools/check_links.py`: non-ASCII file names (quoted by `git ls-files` by default) crashed the checker because the path no longer existed, now `-z`; tracked files deleted from the working tree no longer crash it; `<paths with spaces>` and targets with balanced parentheses parse correctly; example links inside code blocks and inline code are no longer reported.

## 2026-10-24

### Fixed

- `tools/dev_check.ps1`: when `-BaseRef` names a commit that no longer exists (e.g. `github.event.before` after a force-push) the check is skipped, but the leftover `$LASTEXITCODE` made the script exit non-zero and turned the CI Windows gate red; it now ends with an explicit `exit 0` once all gates pass.

### Maintenance

- CI actions are pinned to commit SHAs and bumped to `actions/checkout` v7.0.1 and `actions/setup-python` v7.1.0 (v4/v5 run on the deprecated Node 20); checkout sets `persist-credentials: false`.
- Added `.github/dependabot.yml` (weekly GitHub Actions updates) and a CodeQL workflow (Python, Actions).

## 2026-10-19

### Added

- `ledger.py validate` gains `--json`: structured result (on success `scope`, the `findings` count and per-level counts; on failure an `errors` list), matching `env_check.py --json`; exit code unchanged.
- Extended legal scopes in `toolkit.json` and `ledger.py`: added `competitive-research` (black-box architecture extraction) and `legacy-modernization` (decompilation and migration of orphaned systems).

### Changed

- Restored core project positioning and technical depth: integrated REA technical architecture, cross-modal analysis (Web/Electron IPC, Android ADB/JADX, native call graphs), SaaS moat breakdown, zero-trust client paradigm shift, and 7 production workflows back into bilingual READMEs.
- Removed over-restrictive `ComplianceTextTests` and re-aligned `AGENTS.md` with developer goals and uncompromised quality gates.

## 2026-10-16 (tooling)

### Added

- `env_check.py` and `toolkit.json`: install status, versions and dependencies (JDK, Node, .NET) for 10 reverse-engineering tools, with install commands for missing ones; filter by use case, `--require` as a gate, `--json` output.
- `ledger.py`: evidence ledger validation and Markdown rendering. A legal basis is mandatory; `seen` needs reproducible evidence; `inferred` must trace back to `seen` and never rest on `unknown`; `unknown` needs a next step.
- `templates/agent-prompt.md`, `templates/ledger.example.json`.
- Tests (stdlib `unittest`, 20 cases including a compliance-wording check), `tools/dev_check.ps1`, GitHub Actions (Windows + Ubuntu Python 3.10 / 3.13).
- Bilingual README, MIT license, `.gitattributes`, `.editorconfig`.

### Fixed

- `ledger.py`: a non-string `scope.basis` or `based_on` item is reported as a validation error instead of a TypeError; a non-UTF-8 ledger exits 2.

### Changed

- The original README moved to `docs/background-notes.md`, labelled as reading notes; the tool table moved into the new README and `toolkit.json`.
- Chapter 4 item 6 ("reverse front-end signatures to build an unofficial SDK") rewritten as "add API docs and a client for systems you own". (Restored to the original text on 2026-10-19; see that day's entry on restoring the technical depth.)
- Chapter 4 item 3 ("black-box competitor research") rewritten as "architecture research from public material, without taking apart other people's software"; items 4 and 7 now state authorization and data-ownership conditions.

## 2026-10-16 (initial)

- Notes on 10 AI reverse-engineering tools, REA analysis, clean-room workflow and compliance statement.
