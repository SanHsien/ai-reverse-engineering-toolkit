#!/usr/bin/env python3
"""env_check：檢查本機已安裝哪些逆向分析工具、版本是否夠新，缺的給安裝指令。

工具清單在 toolkit.json。只執行各工具的 --version 之類的唯讀指令，不安裝、不連網。

結束碼：0 = 正常（或 --require 的工具都在）；1 = --require 指定的工具缺少、依賴版本不足或讀不出版本；
2 = 用法錯誤（含 --require 指到只能手動確認的工具）。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CATALOG = Path(__file__).with_name("toolkit.json")
VERSION_RE = re.compile(r"(\d+(?:\.\d+)+|\b\d{2,}\b)")


@dataclass
class Requirement:
    label: str
    status: str  # ok | missing | too-old | unknown | found
    version: str = ""
    min_version: str = ""


@dataclass
class Result:
    id: str
    name: str
    status: str  # found | missing | manual
    version: str = ""
    location: str = ""
    detail: str = ""
    install: str = ""
    requirements: list[Requirement] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return self.status == "found" and all(r.status in ("ok", "found") for r in self.requirements)


# 可替換，讓測試不用真的裝工具
which = shutil.which


def run_version(executable: str, args: list[str]) -> str:
    try:
        proc = subprocess.run([executable, *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (proc.stdout or "") + "\n" + (proc.stderr or "")


def extract_version(output: str) -> str:
    m = VERSION_RE.search(output)
    return m.group(1) if m else ""


def version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:4])


def at_least(version: str, minimum: str) -> bool:
    a, b = version_tuple(version), version_tuple(minimum)
    width = max(len(a), len(b))
    return a + (0,) * (width - len(a)) >= b + (0,) * (width - len(b))


def load_catalog(path: Path = CATALOG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def install_hint(tool: dict) -> str:
    hints = tool.get("install", {})
    key = "windows" if sys.platform == "win32" else ("macos" if sys.platform == "darwin" else "linux")
    return hints.get(key) or hints.get("any", "")


def check_requirement(req: dict) -> Requirement:
    label = req.get("label", req["command"])
    exe = which(req["command"])
    if not exe:
        return Requirement(label, "missing", min_version=req.get("min_version", ""))
    version = extract_version(run_version(exe, req.get("version_args", ["--version"])))
    minimum = req.get("min_version", "")
    if minimum and version and not at_least(version, minimum):
        return Requirement(label, "too-old", version, minimum)
    if minimum and not version:
        # 有版本下限卻讀不出版本（逾時、輸出沒數字）：不能當作符合
        return Requirement(label, "unknown", "", minimum)
    return Requirement(label, "ok" if minimum else "found", version, minimum)


def check_tool(tool: dict, env: dict | None = None) -> Result:
    env = os.environ if env is None else env
    detect = tool.get("detect", {})
    res = Result(tool["id"], tool["name"], "missing", install=install_hint(tool))
    res.requirements = [check_requirement(r) for r in tool.get("requires", [])]
    if "manual" in detect:
        res.status, res.detail = "manual", detect["manual"]
        return res
    if detect.get("env"):
        base = env.get(detect["env"], "")
        if base:
            for rel in detect.get("env_files", []):
                if (Path(base) / rel).is_file():
                    res.status, res.location = "found", str(Path(base) / rel)
                    res.detail = f"{detect['env']}={base}"
                    m = re.search(r"(\d+\.\d+(?:\.\d+)?)", Path(base).name)
                    res.version = m.group(1) if m else ""
                    return res
            res.detail = f"{detect['env']}={base} but none of {', '.join(detect.get('env_files', []))} exists"
    for cmd in detect.get("commands", []):
        exe = which(cmd)
        if exe:
            res.status, res.location = "found", exe
            if detect.get("version_args"):
                res.version = extract_version(run_version(exe, detect["version_args"]))
            return res
    return res


def render_table(results: list[Result]) -> str:
    lines = []
    for r in results:
        mark = {"found": "OK     ", "missing": "MISSING", "manual": "MANUAL "}[r.status]
        if r.status == "found" and not r.ready:
            mark = "PARTIAL"
        head = f"{mark} {r.name}" + (f" {r.version}" if r.version else "")
        lines.append(head)
        if r.location:
            lines.append(f"        at {r.location}")
        if r.detail and r.status != "found":
            lines.append(f"        {r.detail}")
        for q in r.requirements:
            if q.status == "missing":
                lines.append(f"        needs {q.label}: not found")
            elif q.status == "unknown":
                lines.append(f"        needs {q.label}: found, but version unreadable (need {q.min_version}+)")
            elif q.status == "too-old":
                lines.append(f"        needs {q.label}: found {q.version}, too old")
        if r.status == "missing" and r.install:
            lines.append(f"        install: {r.install}")
    found = sum(r.ready for r in results)
    lines.append(f"\n{found}/{len(results)} ready, "
                 f"{sum(r.status == 'manual' for r in results)} need a manual check")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    catalog = load_catalog()
    parser = argparse.ArgumentParser(prog="env_check", description=__doc__.splitlines()[0])
    parser.add_argument("--use-case", choices=sorted(catalog["use_cases"]),
                        help="only tools listed for this legitimate use case")
    parser.add_argument("--require", default="", help="comma-separated tool ids that must be ready (exit 1 otherwise)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    known = {t["id"] for t in catalog["tools"]}
    required = [x.strip() for x in args.require.split(",") if x.strip()]
    manual = sorted(t["id"] for t in catalog["tools"] if "manual" in t.get("detect", {}))
    manual_required = [x for x in required if x in manual]
    if manual_required:
        print(f"ERROR: {', '.join(manual_required)} can only be checked by hand and cannot be required; "
              f"required ids must be auto-detectable (not: {', '.join(manual)})", file=sys.stderr)
        return 2
    unknown = [x for x in required if x not in known]
    if unknown:
        print(f"ERROR: unknown tool id(s): {', '.join(unknown)}; known: {', '.join(sorted(known))}", file=sys.stderr)
        return 2

    tools = [t for t in catalog["tools"] if not args.use_case or args.use_case in t["use_cases"]]
    results = [check_tool(t) for t in tools]
    if args.json:
        print(json.dumps([{**r.__dict__, "ready": r.ready,
                           "requirements": [q.__dict__ for q in r.requirements]} for r in results],
                         ensure_ascii=False, indent=2))
    else:
        if args.use_case:
            print(f"use case: {args.use_case} — {catalog['use_cases'][args.use_case]}\n")
        print(render_table(results))

    by_id = {r.id: r for r in results}
    missing = [x for x in required if x not in by_id or not by_id[x].ready]
    if missing:
        sys.stdout.flush()
        print(f"REQUIRED NOT READY: {', '.join(missing)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
