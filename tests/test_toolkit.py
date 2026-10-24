from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import env_check  # noqa: E402
import ledger  # noqa: E402

EXAMPLE = json.loads((ROOT / "templates" / "ledger.example.json").read_text(encoding="utf-8"))


def capture(fn, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fn(list(args))
    return code, out.getvalue() + err.getvalue()


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = env_check.load_catalog()

    def test_entries_are_complete(self):
        ids = [t["id"] for t in self.catalog["tools"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 10)
        for t in self.catalog["tools"]:
            with self.subTest(t["id"]):
                self.assertRegex(t["repo"], r"^https://github\.com/[\w.-]+/[\w.-]+$")
                self.assertTrue(t["use_cases"])
                self.assertTrue(set(t["use_cases"]) <= set(self.catalog["use_cases"]))
                self.assertTrue(env_check.install_hint(t))
                detect = t["detect"]
                self.assertTrue("manual" in detect or detect.get("commands") or detect.get("env"))

    def test_readme_tables_list_every_tool(self):
        for name in ("README.md", "README.en.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for t in self.catalog["tools"]:
                with self.subTest(readme=name, tool=t["id"]):
                    self.assertIn(t["repo"], text)

    def test_use_cases_match_ledger_bases(self):
        self.assertTrue(set(self.catalog["use_cases"]) <= set(ledger.BASES))


class VersionTests(unittest.TestCase):
    def test_extract(self):
        self.assertEqual(env_check.extract_version('openjdk version "17.0.20" 2026-07-15'), "17.0.20")
        self.assertEqual(env_check.extract_version('openjdk version "21" 2023-09-19'), "21")
        self.assertEqual(env_check.extract_version("v22.19.0"), "22.19.0")
        self.assertEqual(env_check.extract_version("no digits"), "")

    def test_at_least(self):
        self.assertTrue(env_check.at_least("22.19.0", "22.19"))
        self.assertTrue(env_check.at_least("24.1", "22.19"))
        self.assertFalse(env_check.at_least("22.18.9", "22.19"))
        self.assertFalse(env_check.at_least("17.0.20.1", "21"))
        self.assertTrue(env_check.at_least("21", "21"))


class FakeEnv:
    """把 which 與 run_version 換成假的，模擬已安裝的工具。"""

    def __init__(self, installed: dict[str, str]):
        self.installed = installed

    def __enter__(self):
        self._which, self._run = env_check.which, env_check.run_version
        env_check.which = lambda cmd: f"/fake/{cmd}" if cmd in self.installed else None
        env_check.run_version = lambda exe, args: self.installed.get(Path(exe).name, "")
        return self

    def __exit__(self, *exc):
        env_check.which, env_check.run_version = self._which, self._run


def tool(tid):
    return next(t for t in env_check.load_catalog()["tools"] if t["id"] == tid)


class DetectTests(unittest.TestCase):
    def test_found_with_version_and_ok_requirement(self):
        with FakeEnv({"rea-agents": "6.5.0", "node": "v24.11.0"}):
            r = env_check.check_tool(tool("rea"), env={})
        self.assertEqual((r.status, r.version, r.ready), ("found", "6.5.0", True))
        self.assertEqual(r.requirements[0].status, "ok")

    def test_old_dependency_makes_tool_partial(self):
        with FakeEnv({"rea": "6.5.0", "node": "v20.0.0"}):
            r = env_check.check_tool(tool("rea"), env={})
        self.assertEqual(r.status, "found")
        self.assertEqual(r.requirements[0].status, "too-old")
        self.assertFalse(r.ready)
        self.assertIn("PARTIAL", env_check.render_table([r]))

    def test_missing_shows_install_hint(self):
        with FakeEnv({}):
            r = env_check.check_tool(tool("ilspy"), env={})
        self.assertEqual(r.status, "missing")
        self.assertIn("dotnet tool install --global ilspycmd", env_check.render_table([r]))

    def test_ghidra_from_env_var(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            base = tmp / "ghidra_12.0_PUBLIC"
            (base / "support").mkdir(parents=True)
            (base / "support" / "analyzeHeadless").write_text("", encoding="utf-8")
            with FakeEnv({"java": 'openjdk version "21.0.4"'}):
                r = env_check.check_tool(tool("ghidra"), env={"GHIDRA_INSTALL_DIR": str(base)})
                bad = env_check.check_tool(tool("ghidra"), env={"GHIDRA_INSTALL_DIR": str(tmp / "nope")})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual((r.status, r.version, r.ready), ("found", "12.0", True))
        self.assertEqual(bad.status, "missing")
        self.assertIn("none of", bad.detail)

    def test_manual_tools_still_check_requirements(self):
        with FakeEnv({"jadx": "1.5.1"}):
            r = env_check.check_tool(tool("android-re-skill"), env={})
        self.assertEqual(r.status, "manual")
        self.assertEqual([q.status for q in r.requirements], ["found", "missing"])

    def test_cli_require_and_use_case(self):
        with FakeEnv({"ilspycmd": "9.1.0", "dotnet": "8.0.100"}):
            code, out = capture(env_check.main, "--use-case", "data-recovery", "--require", "ilspy")
            self.assertEqual(code, 0, out)
            self.assertNotIn("Frida", out)  # frida 不在 data-recovery
            code, out = capture(env_check.main, "--require", "ilspy,frida")
            self.assertEqual(code, 1)
            self.assertIn("REQUIRED NOT READY: frida", out)
            code, out = capture(env_check.main, "--json")
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertEqual(next(d for d in data if d["id"] == "ilspy")["ready"], True)
            code, out = capture(env_check.main, "--require", "nope")
            self.assertEqual(code, 2)


class LedgerValidateTests(unittest.TestCase):
    def errors(self, mutate):
        doc = copy.deepcopy(EXAMPLE)
        mutate(doc)
        return "\n".join(ledger.validate(doc))

    def test_example_is_valid(self):
        self.assertEqual(ledger.validate(EXAMPLE), [])

    def test_scope_is_mandatory(self):
        self.assertIn("scope is required", self.errors(lambda d: d.pop("scope")))
        self.assertIn("scope.basis must be one of", self.errors(lambda d: d["scope"].update(basis="curiosity")))
        self.assertIn("scope.authorization", self.errors(lambda d: d["scope"].update(authorization="ok")))
        self.assertIn("scope.target", self.errors(lambda d: d["scope"].update(target=" ")))
        self.assertIn("scope.basis must be one of", self.errors(lambda d: d["scope"].update(basis=["defense"])))
        self.assertIn("based_on must be a list of finding ids",
                      self.errors(lambda d: d["findings"][2].update(based_on=[["F2"]])))
        self.assertIn("based_on must be a list of finding ids",
                      self.errors(lambda d: d["findings"][2].update(based_on="F2")))

    def test_seen_needs_reproducible_evidence(self):
        self.assertIn("seen requires at least one evidence",
                      self.errors(lambda d: d["findings"][0].update(evidence=[])))
        self.assertIn("evidence[0].kind",
                      self.errors(lambda d: d["findings"][0]["evidence"][0].update(kind="vibes")))
        self.assertIn("evidence[0].ref is required",
                      self.errors(lambda d: d["findings"][0]["evidence"][0].update(ref="")))

    def test_inferred_rules(self):
        self.assertIn("inferred requires based_on", self.errors(lambda d: d["findings"][2].update(based_on=[])))
        self.assertIn("inferred requires reasoning", self.errors(lambda d: d["findings"][2].update(reasoning="")))
        self.assertIn("missing id 'F9'", self.errors(lambda d: d["findings"][2].update(based_on=["F9"])))
        self.assertIn("cannot be based on unknown finding 'F4'",
                      self.errors(lambda d: d["findings"][2].update(based_on=["F4"])))

    def test_inferred_must_trace_to_seen(self):
        def cycle(d):
            d["findings"] = [f for f in d["findings"] if f["level"] != "seen"]
            d["findings"].append({"id": "F5", "level": "inferred", "claim": "c", "based_on": ["F3"],
                                  "reasoning": "r"})
            d["findings"][0]["based_on"] = ["F5"]
        out = self.errors(cycle)
        self.assertIn("finding F3: does not trace back to any seen finding", out)
        self.assertIn("finding F5: does not trace back", out)

    def test_unknown_needs_next_step_and_ids_unique(self):
        self.assertIn("unknown requires next_step", self.errors(lambda d: d["findings"][3].update(next_step="")))
        self.assertIn("duplicate finding id 'F1'", self.errors(lambda d: d["findings"][1].update(id="F1")))
        self.assertIn("level must be one of", self.errors(lambda d: d["findings"][1].update(level="maybe")))


class LedgerCliTests(unittest.TestCase):
    def test_render_example(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            out = tmp / "report.md"
            code, log = capture(ledger.main, "render", str(ROOT / "templates" / "ledger.example.json"),
                                "-o", str(out))
            self.assertEqual(code, 0, log)
            md = out.read_text(encoding="utf-8")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertIn("已驗證 2 條、推論 1 條、未知 1 條", md)
        self.assertIn("## Seen／已驗證", md)
        self.assertIn("- 根據：F2", md)
        self.assertIn("- 下一步：", md)
        self.assertLess(md.index("## Seen"), md.index("## Inferred"))
        self.assertLess(md.index("## Inferred"), md.index("## Unknown"))

    def test_invalid_ledger_is_not_rendered(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            bad = copy.deepcopy(EXAMPLE)
            bad["scope"]["basis"] = "competitor"
            p = tmp / "bad.json"
            p.write_text(json.dumps(bad), encoding="utf-8")
            code, out = capture(ledger.main, "render", str(p))
            self.assertEqual(code, 1)
            self.assertNotIn("# 舊版記帳軟體", out)
            p.write_text("{not json", encoding="utf-8")
            code, _ = capture(ledger.main, "validate", str(p))
            self.assertEqual(code, 2)
            p.write_bytes('{"title": "舊"}'.encode("cp950"))  # 不是 UTF-8
            code, out = capture(ledger.main, "validate", str(p))
            self.assertEqual(code, 2)
            self.assertIn("cannot read", out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class LedgerJsonTests(unittest.TestCase):
    def test_validate_json_ok(self):
        code, out = capture(ledger.main, "validate", str(ROOT / "templates" / "ledger.example.json"), "--json")
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["findings"], 4)
        self.assertEqual(data["levels"], {"seen": 2, "inferred": 1, "unknown": 1})
        self.assertEqual(data["scope"]["basis"], "data-recovery")

    def test_validate_json_errors(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            bad = copy.deepcopy(EXAMPLE)
            bad["scope"]["basis"] = "competitor"
            p = tmp / "b.json"
            p.write_text(json.dumps(bad), encoding="utf-8")
            code, out = capture(ledger.main, "validate", str(p), "--json")
            self.assertEqual(code, 1)
            data = json.loads(out)
            self.assertFalse(data["ok"])
            self.assertTrue(any("basis" in e for e in data["errors"]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
