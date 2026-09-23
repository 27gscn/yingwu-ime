#!/usr/bin/env python3
"""Generate the Hengma single-character Rime dictionaries.

The normal code forms are:
  pinyin
  pinyin + structure
  pinyin + structure + first-component cue

Structure codes:
  z = left-right / left-middle-right
  s = top-bottom / top-middle-bottom
  b = enclosure / semi-enclosure
  d = single-component
  p = triplicate, overlay, or other special structure
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


BINARY_IDS = set("⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻")
TERNARY_IDS = set("⿲⿳")
ENCLOSURE_IDS = set("⿴⿵⿶⿷⿸⿹⿺")

# Conventional single-component classification takes precedence over a
# mechanical IDS "overlay" reading for these very common integrated forms.
# The list is intentionally conservative; uncertain characters remain in P.
SINGLE_STRUCTURE_OVERRIDES = set(
    "中木本末未米术朱束东车申甲由田王玉井开丰手牛羊生年午果来"
    "夫天大太犬丈支十干于土士工"
    # 〇 has no IDS entry of its own, but it really is a single stroke, so it
    # is named here rather than falling through to the unknown case below.
    "〇"
)


@dataclass(frozen=True)
class Node:
    value: str
    children: tuple["Node", ...] = ()

    @property
    def is_leaf(self) -> bool:
        return not self.children


# Common spoken component names.  The cue is optional, so aliases that share
# an initial are harmless; they only narrow the candidate set.
COMPONENT_CUES: dict[str, tuple[str, str]] = {
    "氵": ("s", "水"),
    "水": ("s", "水"),
    "忄": ("x", "心"),
    "心": ("x", "心"),
    "讠": ("y", "言"),
    "言": ("y", "言"),
    "扌": ("s", "手"),
    "手": ("s", "手"),
    "钅": ("j", "金"),
    "金": ("j", "金"),
    "艹": ("c", "草"),
    "亻": ("r", "人"),
    "人": ("r", "人"),
    "宀": ("b", "宝盖"),
    "冖": ("b", "宝盖"),
    "疒": ("b", "病"),
    "辶": ("z", "走之"),
    "廴": ("z", "走之"),
    "阝": ("e", "耳刀"),
    "礻": ("s", "示"),
    "衤": ("y", "衣"),
    "衣": ("y", "衣"),
    "饣": ("s", "食"),
    "食": ("s", "食"),
    "纟": ("s", "丝"),
    "糹": ("s", "丝"),
    "刂": ("d", "刀"),
    "刀": ("d", "刀"),
    "灬": ("h", "火"),
    "火": ("h", "火"),
    "冫": ("b", "冰"),
    "犭": ("q", "犬"),
    "犬": ("q", "犬"),
    "攵": ("w", "文"),
    "攴": ("w", "文"),
    "竹": ("z", "竹"),
    "⺮": ("z", "竹"),
    "罒": ("w", "网"),
    "网": ("w", "网"),
    "囗": ("k", "框"),
    "广": ("g", "广"),
    "门": ("m", "门"),
    "門": ("m", "门"),
    "口": ("k", "口"),
    "日": ("r", "日"),
    "月": ("y", "月"),
    "木": ("m", "木"),
    "土": ("t", "土"),
    "石": ("s", "石"),
    "米": ("m", "米"),
    "女": ("n", "女"),
    "王": ("w", "王"),
    "玉": ("y", "玉"),
    "贝": ("b", "贝"),
    "貝": ("b", "贝"),
    "目": ("m", "目"),
    "虫": ("c", "虫"),
    "禾": ("h", "禾"),
    "足": ("z", "足"),
    "子": ("z", "子"),
    "大": ("d", "大"),
    "小": ("x", "小"),
    "山": ("s", "山"),
    "雨": ("y", "雨"),
    "耳": ("e", "耳"),
    "车": ("c", "车"),
    "車": ("c", "车"),
    "马": ("m", "马"),
    "馬": ("m", "马"),
    "鱼": ("y", "鱼"),
    "魚": ("y", "鱼"),
    "鸟": ("n", "鸟"),
    "鳥": ("n", "鸟"),
    "页": ("y", "页"),
    "頁": ("y", "页"),
}


def strip_tone(text: str) -> str:
    text = text.lower().replace("ü", "v").replace("u:", "v")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def parse_ids(text: str) -> Node | None:
    """Parse one IDS expression. Unknown markers remain leaves."""
    if not text or text == "？":
        return None

    def parse_at(i: int) -> tuple[Node, int]:
        if i >= len(text):
            raise ValueError("unexpected end")
        token = text[i]
        if token in BINARY_IDS:
            left, j = parse_at(i + 1)
            right, k = parse_at(j)
            return Node(token, (left, right)), k
        if token in TERNARY_IDS:
            first, j = parse_at(i + 1)
            second, k = parse_at(j)
            third, m = parse_at(k)
            return Node(token, (first, second, third)), m
        return Node(token), i + 1

    try:
        node, _ = parse_at(0)
        return node
    except (ValueError, IndexError):
        return None


def first_leaf(node: Node | None) -> str | None:
    if node is None:
        return None
    if node.is_leaf:
        return None if node.value == "？" else node.value
    for child in node.children:
        leaf = first_leaf(child)
        if leaf:
            return leaf
    return None


def same_tree(a: Node, b: Node) -> bool:
    return a == b


def triplicate_component(node: Node | None) -> Node | None:
    """Detect 品/森/晶/众-style threefold layouts."""
    if node is None or node.is_leaf:
        return None
    # X above X X
    if node.value == "⿱" and len(node.children) == 2:
        top, bottom = node.children
        if (
            bottom.value == "⿰"
            and len(bottom.children) == 2
            and same_tree(top, bottom.children[0])
            and same_tree(top, bottom.children[1])
        ):
            return top
        # X X above X
        if (
            top.value == "⿰"
            and len(top.children) == 2
            and same_tree(top.children[0], top.children[1])
            and same_tree(top.children[0], bottom)
        ):
            return bottom
    return None


def classify_structure(
    node: Node | None, character: str | None = None
) -> tuple[str, str | None]:
    """Return (structure code, first component leaf)."""
    if character in SINGLE_STRUCTURE_OVERRIDES:
        return "d", first_leaf(node) or character
    if node is None:
        # No decomposition data at all. "Unknown" is not the same claim as
        # 独体 -- 𰻝 has no IDS entry and some fifty strokes -- so an
        # unclassifiable character joins p, the bucket for everything that
        # does not fit the four named shapes, rather than being asserted to
        # be a single component.
        return "p", None
    if node.is_leaf:
        return "d", first_leaf(node)

    triple = triplicate_component(node)
    if triple is not None:
        return "p", first_leaf(triple)

    op = node.value
    if op in {"⿰", "⿲"}:
        return "z", first_leaf(node.children[0])
    if op in {"⿱", "⿳"}:
        return "s", first_leaf(node.children[0])
    if op in ENCLOSURE_IDS:
        return "b", first_leaf(node.children[0])
    if op == "⿻":
        return "p", first_leaf(node.children[0])
    return "p", first_leaf(node.children[0]) if node.children else None


def load_structure_data(path: Path):
    rows: dict[str, dict] = {}
    component_pinyin: dict[str, list[str]] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            char = row.get("character")
            if not char:
                continue
            rows[char] = row
            component_pinyin[char] = [
                strip_tone(p) for p in row.get("pinyin", []) if p
            ]
    return rows, component_pinyin


def load_cjkvi_ids(path: Path | None) -> dict[str, str]:
    """Load the first generic IDS expression for each character."""
    if path is None:
        return {}
    result: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for raw in f:
            if not raw or raw.startswith("#"):
                continue
            fields = raw.rstrip("\n").split("\t")
            if len(fields) < 3 or not fields[1]:
                continue
            char = fields[1]
            ids = re.sub(r"\[[A-Z]+\]$", "", fields[2])
            if ids:
                result[char] = ids
    return result


def component_cue(
    component: str | None,
    radical: str | None,
    component_pinyin: dict[str, list[str]],
) -> tuple[str | None, str | None]:
    # Use the dictionary radical first; fall back to the visually first
    # component only when the radical has no usable mnemonic code.
    for candidate in (radical, component):
        if not candidate:
            continue
        if candidate in COMPONENT_CUES:
            return COMPONENT_CUES[candidate]
        readings = component_pinyin.get(candidate, [])
        if readings and readings[0]:
            return readings[0][0], candidate
    return None, None


def load_8105(path: Path):
    entries: list[tuple[str, str, int]] = []
    body = False
    with path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line == "...":
                body = True
                continue
            if not body or not line or line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 2:
                continue
            char, pinyin = fields[:2]
            if len(char) != 1 or not re.fullmatch(r"[a-zv]+", pinyin):
                continue
            try:
                weight = int(fields[2]) if len(fields) > 2 else 1
            except ValueError:
                weight = 1
            entries.append((char, pinyin, max(weight, 1)))
    return entries


def typo_aliases(pinyin: str, valid_pinyin: set[str]) -> set[str]:
    """Conservative typo aliases: adjacent transposition and one omission.

    Aliases that are already a valid pinyin syllable are skipped, preventing
    typo correction from overwhelming legitimate syllables.
    """
    aliases: set[str] = set()
    chars = list(pinyin)
    for i in range(len(chars) - 1):
        if chars[i] == chars[i + 1]:
            continue
        swapped = chars.copy()
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        aliases.add("".join(swapped))
    if len(pinyin) >= 4:
        for i in range(len(pinyin)):
            aliases.add(pinyin[:i] + pinyin[i + 1 :])
    return {
        alias
        for alias in aliases
        if len(alias) >= 2
        and alias != pinyin
        and alias not in valid_pinyin
        and re.fullmatch(r"[a-zv]+", alias)
    }


def yaml_header(name: str, version: str, imports: list[str] | None = None) -> str:
    import_block = ""
    if imports:
        import_block = "import_tables:\n" + "".join(f"  - {x}\n" for x in imports)
    return (
        "# Rime dictionary\n"
        "# encoding: utf-8\n"
        "# Generated by Hengma dictionary compiler.\n"
        "---\n"
        f"name: {name}\n"
        f'version: "{version}"\n'
        "sort: by_weight\n"
        f"{import_block}"
        "...\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hanzi-data", type=Path, required=True)
    ap.add_argument("--cjkvi-ids", type=Path)
    ap.add_argument("--rime-8105", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--version", default="0.1.0")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    structure_rows, component_pinyin = load_structure_data(args.hanzi_data)
    fallback_ids = load_cjkvi_ids(args.cjkvi_ids)
    entries = load_8105(args.rime_8105)
    valid_pinyin = {p for _, p, _ in entries}

    main_rows: dict[tuple[str, str], int] = {}
    fuzzy_rows: dict[tuple[str, str], int] = {}
    metadata: list[dict] = []
    structure_counts = {k: 0 for k in "zsbpd"}
    missing_structure: list[str] = []
    cue_count = 0

    for char, pinyin, weight in entries:
        info = structure_rows.get(char)
        primary_ids = info.get("decomposition", "") if info else ""
        ids = (
            fallback_ids.get(char, "")
            if not primary_ids or primary_ids == "？"
            else primary_ids
        )
        node = parse_ids(ids)
        structure, first_component = classify_structure(node, char)
        if node is None:
            missing_structure.append(char)
        structure_counts[structure] += 1

        radical = info.get("radical") if info else None
        cue, cue_label = component_cue(
            first_component, radical, component_pinyin
        )
        if cue:
            cue_count += 1

        normal_codes = [pinyin, pinyin + structure]
        if cue:
            normal_codes.append(pinyin + structure + cue)

        for code in normal_codes:
            key = (char, code)
            main_rows[key] = max(main_rows.get(key, 0), weight)

        for typo in typo_aliases(pinyin, valid_pinyin):
            typo_codes = [typo, typo + structure]
            if cue:
                typo_codes.append(typo + structure + cue)
            for code in typo_codes:
                key = (char, code)
                fuzzy_rows[key] = max(
                    fuzzy_rows.get(key, 0), max(1, weight // 100)
                )

        metadata.append(
            {
                "character": char,
                "pinyin": pinyin,
                "structure": structure,
                "first_component": first_component,
                "cue": cue,
                "cue_label": cue_label,
                "codes": normal_codes,
                "weight": weight,
            }
        )

    main_path = args.out_dir / "hengma.dict.yaml"
    fuzzy_path = args.out_dir / "hengma_fuzzy.dict.yaml"
    meta_path = args.out_dir / "hengma_codes.jsonl"

    with main_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(
            yaml_header(
                "hengma", args.version, ["hengma_fuzzy", "hengma_phrases"]
            )
        )
        for (char, code), weight in sorted(
            main_rows.items(), key=lambda x: (x[0][1], -x[1], x[0][0])
        ):
            f.write(f"{char}\t{code}\t{weight}\n")

    with fuzzy_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(yaml_header("hengma_fuzzy", args.version))
        for (char, code), weight in sorted(
            fuzzy_rows.items(), key=lambda x: (x[0][1], -x[1], x[0][0])
        ):
            f.write(f"{char}\t{code}\t{weight}\n")

    with meta_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in metadata:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "source_entries": len(entries),
        "main_rows": len(main_rows),
        "fuzzy_rows": len(fuzzy_rows),
        "structure_counts": structure_counts,
        "missing_structure_entries": len(missing_structure),
        "entries_with_cue": cue_count,
        "output": {
            "main": str(main_path),
            "fuzzy": str(fuzzy_path),
            "metadata": str(meta_path),
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()