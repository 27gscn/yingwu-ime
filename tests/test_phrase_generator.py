from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "generate_phrases", ROOT / "data-tools" / "generate_phrases.py"
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)
Entry = module.Entry


class PhraseDisambiguationTests(unittest.TestCase):
    def test_approved_today_example(self):
        rows = [
            Entry("今天去哪了", "jintianqunale", tuple(), 100),
            Entry("今天去拿了", "jintianqunale", tuple(), 10),
        ]
        char_info = {"哪": ("z", "k"), "拿": ("s", "s")}
        _, effective, decisions = module.disambiguate_group(
            rows, char_info, max_levels=2
        )
        self.assertEqual(
            effective[rows[0]], "jintianqunalezk"
        )
        self.assertEqual(
            effective[rows[1]], "jintianqunaless"
        )
        self.assertEqual(decisions[0]["position"], 3)

    def test_second_pair_is_only_added_to_residual_branch(self):
        first = Entry("甲甲", "same", tuple(), 100)
        second = Entry("由乙", "same", tuple(), 90)
        third = Entry("拿拿", "same", tuple(), 80)
        char_info = {
            "甲": ("d", "j"),
            "由": ("d", "j"),
            "乙": ("s", "y"),
            "拿": ("s", "s"),
        }
        generated, effective, decisions = module.disambiguate_group(
            [first, second, third], char_info, max_levels=2
        )
        self.assertEqual(effective[first], "samedjdj")
        self.assertEqual(effective[second], "samedjsy")
        self.assertEqual(effective[third], "samess")
        self.assertEqual(len(generated[first]), 2)
        self.assertEqual(len(generated[third]), 1)
        self.assertEqual([item["level"] for item in decisions], [1, 2])

    def test_one_level_preserves_collision_for_comparison(self):
        first = Entry("甲甲", "same", tuple(), 100)
        second = Entry("由乙", "same", tuple(), 90)
        third = Entry("拿拿", "same", tuple(), 80)
        info = {
            "甲": ("d", "j"),
            "由": ("d", "j"),
            "乙": ("s", "y"),
            "拿": ("s", "s"),
        }
        _, effective, _ = module.disambiguate_group(
            [first, second, third], info, max_levels=1
        )
        self.assertEqual(effective[first], effective[second])
        self.assertNotEqual(effective[first], effective[third])

    def test_unique_phrase_keeps_plain_code(self):
        entry = Entry("数字法治", "shuzifazhi", tuple(), 100)
        _, effective, decisions = module.disambiguate_group(
            [entry], {}, max_levels=2
        )
        self.assertEqual(effective[entry], "shuzifazhi")
        self.assertEqual(decisions, [])

    def test_prefix_length_collision_is_not_falsely_resolved(self):
        first = Entry("甲乙", "same", tuple(), 100)
        second = Entry("甲乙甲", "same", tuple(), 90)
        info = {"甲": ("d", "j"), "乙": ("d", "y")}
        _, effective, decisions = module.disambiguate_group(
            [first, second], info, max_levels=2
        )
        self.assertEqual(effective[first], "same")
        self.assertEqual(effective[second], "same")
        self.assertEqual(decisions, [])


if __name__ == "__main__":
    unittest.main()
