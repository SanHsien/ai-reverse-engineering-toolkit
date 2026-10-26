"""壞輸入不能讓檢查器當掉或輸出走樣：結束碼語意與 Markdown 結構要守住。"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import check_links  # noqa: E402
import ledger  # noqa: E402

EXAMPLE = json.loads((ROOT / "templates" / "ledger.example.json").read_text(encoding="utf-8"))
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")


def capture(fn, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fn(list(args))
    return code, out.getvalue() + err.getvalue()


def with_example(mutate):
    doc = copy.deepcopy(EXAMPLE)
    mutate(doc)
    return doc


class LedgerValidateRobustness(unittest.TestCase):
    def test_unhashable_evidence_kind_is_a_validation_error(self):
        for bad in (["command"], {"a": 1}):
            with self.subTest(kind=bad):
                doc = with_example(lambda d: d["findings"][0]["evidence"][0].update(kind=bad))
                self.assertTrue(any("evidence[0].kind" in e for e in ledger.validate(doc)))

    def test_long_inference_chain_does_not_overflow_the_stack(self):
        def chain(d):
            for i in range(3000):
                prev = "F2" if i == 0 else f"C{i - 1}"
                d["findings"].append({"id": f"C{i}", "level": "inferred", "claim": "c",
                                      "based_on": [prev], "reasoning": "r"})
        self.assertEqual(ledger.validate(with_example(chain)), [])

    def test_ungrounded_diamond_ladder_finishes(self):
        def ladder(d):
            d["findings"] = [f for f in d["findings"] if f["level"] != "seen"]
            d["findings"][0]["based_on"] = ["L0a", "L0b"]  # F3 掛在梯子頂端
            for i in range(60):
                below = ["L%da" % (i + 1), "L%db" % (i + 1)] if i < 59 else ["F4"]
                for side in "ab":
                    d["findings"].append({"id": f"L{i}{side}", "level": "inferred", "claim": "c",
                                          "based_on": below, "reasoning": "r"})
        errors = ledger.validate(with_example(ladder))
        self.assertTrue(any("does not trace back" in e for e in errors))


class LedgerRenderRobustness(unittest.TestCase):
    def render(self, mutate):
        return ledger.render(with_example(mutate))

    def test_backticks_in_evidence_ref_keep_the_code_span_intact(self):
        ref = "echo `id` | grep uid"
        md = self.render(lambda d: d["findings"][0]["evidence"][0].update(ref=ref))
        row = next(line for line in md.splitlines() if line.startswith("| file-offset"))
        cell = row.split(" | ")[1].replace("\|", "|")
        self.assertEqual(CODE_SPAN.search(cell).group(2).strip(), ref)

    def test_newlines_cannot_start_new_headings_or_bullets(self):
        def mutate(d):
            d["title"] = "報告\n# 假標題"
            d["scope"]["target"] = "目標\n## 假章節"
            d["findings"][0]["claim"] = "主張\n### 假小節"
            d["findings"][2]["reasoning"] = "推理\n## 假章節二"
            d["findings"][3]["next_step"] = "下一步\n# 假標題二"
        md = self.render(mutate)
        for line in md.splitlines():
            self.assertNotRegex(line, r"^#+ 假")

    def test_unwritable_output_exits_2_with_message(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            target = tmp / "missing-dir" / "out.md"
            code, out = capture(ledger.main, "render", str(ROOT / "templates" / "ledger.example.json"),
                                "-o", str(target))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(code, 2)
        self.assertIn("cannot write", out)


class LinkCheckRobustness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        subprocess.run(["git", "-C", str(self.tmp), "init", "-q"], check=True)
        self._root = check_links.ROOT
        check_links.ROOT = self.tmp

    def tearDown(self):
        check_links.ROOT = self._root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name, text=""):
        path = self.tmp / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_main(self):
        return capture(lambda _argv: check_links.main())

    def test_non_ascii_file_names_are_listed_and_checked(self):
        self.write("文件.md", "[ok](other.md)\n")
        self.write("other.md")
        code, out = self.run_main()
        self.assertEqual(code, 0, out)
        self.assertIn("文件.md", out)

    def test_angle_bracket_link_with_spaces(self):
        self.write("a.md", "[x](<my file.md>)\n")
        self.write("my file.md")
        code, out = self.run_main()
        self.assertEqual(code, 0, out)

    def test_parentheses_in_target(self):
        self.write("a.md", "[x](notes_(v2).md)\n")
        self.write("notes_(v2).md")
        code, out = self.run_main()
        self.assertEqual(code, 0, out)

    def test_examples_in_code_are_not_links(self):
        self.write("a.md", "```md\n[x](nope.md)\n```\n\n行內 `[y](nope2.md)` 範例\n")
        code, out = self.run_main()
        self.assertEqual(code, 0, out)

    def test_real_broken_link_still_fails(self):
        self.write("a.md", "[x](nope.md)\n\n```\n[y](ignored.md)\n```\n")
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("nope.md", out)
        self.assertNotIn("ignored.md", out)

    def test_tracked_file_deleted_from_disk_does_not_crash(self):
        path = self.write("gone.md", "x\n")
        self.write("keep.md")
        subprocess.run(["git", "-C", str(self.tmp), "add", "."], check=True)
        path.unlink()
        code, out = self.run_main()
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
