#!/usr/bin/env python3
"""ledger：證據分層回報（Seen／Inferred／Unknown）的檢查與轉成 Markdown。

讓 AI agent 把逆向分析結論寫成 JSON 帳本，再用本工具機械檢查：
- 開頭必須宣告分析範圍與合法依據（自己的軟體、互通性、資料救援、資安防禦、經授權測試）
- Seen（親眼看到）必須附可重現的證據：檔案偏移、檔案行號、指令、封包紀錄、截圖
- Inferred（推論）必須指出根據哪幾條結論，而且最終要追溯到至少一條 Seen
- Unknown（未知）必須寫下一步怎麼查
- 結論不得建立在 Unknown 上

子指令：
  validate <ledger.json>             檢查，結束碼 0 = 通過、1 = 有錯、2 = 檔案讀不到或不是 JSON
  render   <ledger.json> [-o out.md] 檢查通過才輸出 Markdown
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

BASES = {
    "own-software": "自己擁有或開發的軟體",
    "authorized-test": "取得書面授權的測試",
    "interoperability": "法律允許範圍內的互通性",
    "data-recovery": "救援自己擁有的資料",
    "defense": "資安防禦（可疑樣本、自家產品防護驗證）",
    "competitive-research": "競品黑箱架構調研（提取規格與架構設計）",
    "legacy-modernization": "無原始碼老舊系統維護與現代化遷移",
}
EVIDENCE_KINDS = {"file-offset", "file-line", "command", "capture", "screenshot"}
LEVELS = ("seen", "inferred", "unknown")
LABELS = {"seen": "Seen／已驗證", "inferred": "Inferred／推論", "unknown": "Unknown／未知"}


def validate(doc: object) -> list[str]:
    errors: list[str] = []
    doc = copy.deepcopy(doc)  # 下面會把壞掉的 based_on 清空，不能動到呼叫者的資料
    if not isinstance(doc, dict):
        return ["ledger must be a JSON object"]
    if not str(doc.get("title", "")).strip():
        errors.append("title is required")

    scope = doc.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope is required: {target, basis, authorization}")
    else:
        if not str(scope.get("target", "")).strip():
            errors.append("scope.target is required (what is being analyzed)")
        if not isinstance(scope.get("basis"), str) or scope["basis"] not in BASES:
            errors.append(f"scope.basis must be one of: {', '.join(BASES)}")
        if len(str(scope.get("authorization", "")).strip()) < 10:
            errors.append("scope.authorization must explain why you may analyze this target (10+ characters)")

    findings = doc.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("findings must be a non-empty list")
        return errors

    by_id: dict[str, dict] = {}
    for i, f in enumerate(findings):
        where = f"findings[{i}]"
        if not isinstance(f, dict):
            errors.append(f"{where} must be an object")
            continue
        fid = str(f.get("id", "")).strip()
        if not fid:
            errors.append(f"{where}.id is required")
        elif fid in by_id:
            errors.append(f"duplicate finding id {fid!r}")
        else:
            by_id[fid] = f
        where = f"finding {fid or i}"
        level = f.get("level")
        if level not in LEVELS:
            errors.append(f"{where}: level must be one of {', '.join(LEVELS)}")
            continue
        if not str(f.get("claim", "")).strip():
            errors.append(f"{where}: claim is required")
        if level == "seen":
            ev = f.get("evidence")
            if not isinstance(ev, list) or not ev:
                errors.append(f"{where}: seen requires at least one evidence item")
            else:
                for j, e in enumerate(ev):
                    if not isinstance(e, dict) or e.get("kind") not in EVIDENCE_KINDS:
                        errors.append(f"{where}: evidence[{j}].kind must be one of {', '.join(sorted(EVIDENCE_KINDS))}")
                    elif not str(e.get("ref", "")).strip():
                        errors.append(f"{where}: evidence[{j}].ref is required (offset, path:line, command, ...)")
        elif level == "inferred":
            deps = f.get("based_on")
            if not deps:
                errors.append(f"{where}: inferred requires based_on (ids of the findings it relies on)")
            elif not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
                errors.append(f"{where}: based_on must be a list of finding ids (strings)")
                f["based_on"] = []  # 後面的追溯檢查會把它報成沒有根據
            if not str(f.get("reasoning", "")).strip():
                errors.append(f"{where}: inferred requires reasoning")
        elif not str(f.get("next_step", "")).strip():
            errors.append(f"{where}: unknown requires next_step (how to find out)")

    for fid, f in by_id.items():
        if f.get("level") != "inferred":
            continue
        for dep in f.get("based_on") or []:
            if dep not in by_id:
                errors.append(f"finding {fid}: based_on references missing id {dep!r}")
            elif by_id[dep].get("level") == "unknown":
                errors.append(f"finding {fid}: cannot be based on unknown finding {dep!r}")
        if not _grounded(fid, by_id, set()):
            errors.append(f"finding {fid}: does not trace back to any seen finding (or has a cycle)")
    return errors


def _grounded(fid: str, by_id: dict[str, dict], visiting: set[str]) -> bool:
    f = by_id.get(fid)
    if f is None or fid in visiting:
        return False
    if f.get("level") == "seen":
        return True
    if f.get("level") != "inferred":
        return False
    visiting = visiting | {fid}
    return any(_grounded(d, by_id, visiting) for d in f.get("based_on") or [])


def _cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def render(doc: dict) -> str:
    scope = doc["scope"]
    findings = doc["findings"]
    counts = {lv: sum(f["level"] == lv for f in findings) for lv in LEVELS}
    lines = [
        f"# {doc['title']}",
        "",
        f"- 分析對象：{scope['target']}",
        f"- 合法依據：{BASES[scope['basis']]}（`{scope['basis']}`）",
        f"- 授權說明：{scope['authorization']}",
    ]
    if scope.get("date"):
        lines.append(f"- 日期：{scope['date']}")
    lines += ["", f"結論：已驗證 {counts['seen']} 條、推論 {counts['inferred']} 條、未知 {counts['unknown']} 條。", ""]

    for level in LEVELS:
        items = [f for f in findings if f["level"] == level]
        if not items:
            continue
        lines += [f"## {LABELS[level]}", ""]
        for f in items:
            lines.append(f"### [{f['id']}] {f['claim']}")
            lines.append("")
            if level == "seen":
                lines += ["| 類型 | 位置／指令 | 說明 |", "|---|---|---|"]
                for e in f["evidence"]:
                    lines.append(f"| {e['kind']} | `{_cell(e['ref'])}` | {_cell(e.get('note', ''))} |")
            elif level == "inferred":
                lines.append(f"- 根據：{', '.join(f['based_on'])}")
                lines.append(f"- 推理：{f['reasoning']}")
                if f.get("confidence"):
                    lines.append(f"- 信心：{f['confidence']}")
            else:
                lines.append(f"- 下一步：{f['next_step']}")
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="ledger", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate")
    v.add_argument("ledger")
    v.add_argument("--json", action="store_true", help="emit the result as JSON (exit code unchanged)")
    r = sub.add_parser("render")
    r.add_argument("ledger")
    r.add_argument("-o", "--output", help="write Markdown here instead of stdout")
    args = parser.parse_args(argv)
    as_json = getattr(args, "json", False)

    try:
        doc = json.loads(Path(args.ledger).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        message = f"cannot read {args.ledger}: {exc}"
        if as_json:
            print(json.dumps({"ok": False, "errors": [message]}, ensure_ascii=False, indent=2))
        else:
            print(f"ERROR: {message}", file=sys.stderr)
        return 2
    errors = validate(doc)
    if errors:
        if as_json:
            print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        else:
            for e in errors:
                print(f"ERROR: {e}")
            print(f"FAILED: {len(errors)} error(s)")
        return 1
    if args.command == "validate":
        if as_json:
            findings = doc["findings"]
            print(json.dumps({
                "ok": True,
                "scope": doc["scope"],
                "findings": len(findings),
                "levels": {lv: sum(f["level"] == lv for f in findings) for lv in LEVELS},
            }, ensure_ascii=False, indent=2))
        else:
            print(f"OK: {len(doc['findings'])} finding(s), scope {doc['scope']['basis']}")
        return 0
    text = render(doc)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
