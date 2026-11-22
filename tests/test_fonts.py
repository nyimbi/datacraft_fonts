# pyright: reportAttributeAccessIssue=false
"""Gate on the built fonts. Run `uv run build.py` first.

	uv run --with pytest --with fonttools --with brotli pytest -q tests
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402  # pyright: ignore[reportMissingImports]

UPSTREAM_NAMES = ("STIX", "Fira", "JetBrains", "TM Math")
MANIFEST = json.loads((ROOT / "fonts" / "manifest.json").read_text())
BUILT = sorted((ROOT / "fonts" / "desktop").rglob("*.[ot]tf")) + sorted((ROOT / "fonts" / "web").glob("*.woff2"))


def name_leaks(font: TTFont) -> list[tuple[int, str]]:
	"""Family-name records that still carry an upstream name."""
	ids = set(build.RENAMED_IDS) | {r.nameID for r in font["name"].names if r.nameID > 255}
	leaks = [
		(r.nameID, r.toUnicode())
		for r in font["name"].names
		if r.nameID in ids and any(u in r.toUnicode() for u in UPSTREAM_NAMES)
	]
	if "CFF " in font:
		cff = font["CFF "].cff
		top = cff.topDictIndex[0]
		for label, val in (("cff-name", cff.fontNames[0]), ("FamilyName", getattr(top, "FamilyName", "")), ("FullName", getattr(top, "FullName", ""))):
			if any(u in (val or "") for u in UPSTREAM_NAMES):
				leaks.append((-1, f"{label}={val}"))
	return leaks


def test_every_source_was_built() -> None:
	expected = sum(len(f.files) for f in build.FAMILIES)
	assert len(MANIFEST) == expected
	variable = sum(1 for f in build.FAMILIES for s in f.files if "[wght]" in s)
	assert len(BUILT) == 2 * expected + len(build.STATIC_WEIGHTS) * variable


@pytest.mark.parametrize("path", BUILT, ids=lambda p: p.name)
def test_no_upstream_name_in_family_records(path: Path) -> None:
	assert name_leaks(TTFont(path)) == []


@pytest.mark.parametrize("path", BUILT, ids=lambda p: p.name)
def test_shared_vertical_metrics(path: Path) -> None:
	f = TTFont(path)
	os2, hhea, head = f["OS/2"], f["hhea"], f["head"]
	assert (os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) == (build.ASCENDER, build.DESCENDER, 0)
	assert (hhea.ascent, hhea.descent, hhea.lineGap) == (build.ASCENDER, build.DESCENDER, 0)
	assert os2.fsSelection & (1 << 7)
	assert os2.usWinAscent >= head.yMax and os2.usWinDescent >= -head.yMin


@pytest.mark.parametrize("path", BUILT, ids=lambda p: p.name)
def test_licence_and_copyright_kept(path: Path) -> None:
	f = TTFont(path)
	assert "open font license" in (f["name"].getDebugName(13) or "").lower()
	assert "copyright" in (f["name"].getDebugName(0) or "").lower()


@pytest.mark.parametrize("slug", ["math", "sans-math"])
def test_math_fonts_keep_math_table(slug: str) -> None:
	for path in (ROOT / "fonts" / "desktop" / slug).glob("*.[ot]tf"):
		math = TTFont(path)["MATH"].table
		assert math.MathConstants.AxisHeight.Value > 0


def test_canary_leak_check_sees_upstream_names() -> None:
	"""The leak predicate must fire on every unmodified upstream font."""
	for fam in build.FAMILIES:
		src = build.UPSTREAM / fam.upstream_dir / fam.files[0]
		assert name_leaks(TTFont(src)), src.name
