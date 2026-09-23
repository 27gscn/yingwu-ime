from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class RuntimeDataTests(unittest.TestCase):
    def test_schema_is_self_contained_and_static(self):
        schema = (DATA / "hengma.schema.yaml").read_text(encoding="utf-8")
        self.assertNotIn("import_preset", schema)
        self.assertIn("enable_sentence: false", schema)
        self.assertIn("enable_user_dict: false", schema)
        self.assertIn("max_phrase_length: 12", schema)
        self.assertIn("max_code_length: 96", schema)

    def test_main_dictionary_imports_required_tables(self):
        main = (DATA / "hengma.dict.yaml").read_text(
            encoding="utf-8", errors="strict"
        )
        self.assertIn("  - hengma_fuzzy", main)
        self.assertIn("  - hengma_phrases", main)

    def test_phrase_dictionary_rows_and_examples(self):
        path = DATA / "hengma_phrases.dict.yaml"
        body = False
        rows = 0
        maximum = 0
        examples = set()
        with path.open(encoding="utf-8") as source:
            for raw in source:
                line = raw.rstrip("\n")
                if line == "...":
                    body = True
                    continue
                if not body or not line:
                    continue
                text, code, weight = line.split("\t")
                self.assertTrue(2 <= len(text) <= 12)
                self.assertRegex(code, r"^[a-z]+$")
                self.assertGreaterEqual(int(weight), 1)
                maximum = max(maximum, len(code))
                rows += 1
                if text in {"今天去哪了", "今天去拿了"}:
                    examples.add((text, code))
        self.assertEqual(rows, 696_515)
        self.assertLessEqual(maximum, 96)
        self.assertIn(("今天去哪了", "jintianqunalezk"), examples)
        self.assertIn(("今天去拿了", "jintianqunaless"), examples)


if __name__ == "__main__":
    unittest.main()
