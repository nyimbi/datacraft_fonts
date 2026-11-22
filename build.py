# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools>=4.50", "brotli>=1.1"]
# ///
# pyright: reportAttributeAccessIssue=false
# fontTools table attributes are set dynamically from struct formats.
"""Build the Datacraft font family from the OFL upstream sources in sources/upstream.

Each family is renamed (OFL section 3 requires modified versions to drop the
upstream names), given one shared set of vertical metrics so mixed text, math and
code share a baseline grid, and written as desktop TTF/OTF plus web WOFF2.

	uv run build.py
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "sources" / "upstream"
OUT_DESKTOP = ROOT / "fonts" / "desktop"
OUT_WEB = ROOT / "fonts" / "web"
VERSION = "1.000"
VENDOR = "DTCR"

# Shared vertical metrics, in units of a 1000-unit em. Every source font is 1000 UPM.
# 900 + 300 gives a CSS `line-height: normal` of 1.2 and puts the baseline at the
# same height in every family's line box.
ASCENDER = 900
DESCENDER = -300

# Name IDs that carry the family name. Copyright (0), trademark (7), manufacturer (8),
# designer (9), license (13/14) are left as upstream wrote them.
RENAMED_IDS = {1, 3, 4, 6, 16, 17, 18, 20, 21, 22, 25}


@dataclass(frozen=True)
class Family:
	slug: str
	name: str
	upstream_dir: str
	upstream_name: str
	files: tuple[str, ...]
	role: str
	css_weight: str = "400"
	license_file: str = "OFL.txt"
	extra_renames: tuple[tuple[str, str], ...] = field(default_factory=tuple)

	@property
	def ps(self) -> str:
		return self.name.replace(" ", "")

	@property
	def upstream_ps(self) -> str:
		return self.upstream_name.replace(" ", "")

	def renames(self) -> list[tuple[str, str]]:
		return [(self.upstream_name, self.name), (self.upstream_ps, self.ps), *self.extra_renames]


FIRA_WEIGHTS = ("Light", "Regular", "Medium", "SemiBold", "Bold")
FAMILIES: tuple[Family, ...] = (
	Family(
		slug="serif",
		name="Datacraft Serif",
		upstream_dir="stix-two-text",
		upstream_name="STIX Two Text",
		files=("STIXTwoText[wght].ttf", "STIXTwoText-Italic[wght].ttf"),
		role="Body text for papers, long-form posts and anything set next to math",
		css_weight="400 700",
	),
	Family(
		slug="math",
		name="Datacraft Math",
		upstream_dir="stix-two-math",
		upstream_name="STIX Two Math",
		files=("STIXTwoMath-Regular.ttf",),
		role="OpenType MATH companion to Datacraft Serif",
	),
	Family(
		slug="sans",
		name="Datacraft Sans",
		upstream_dir="fira-sans",
		upstream_name="Fira Sans",
		files=tuple(
			f"FiraSans-{w}{s}.ttf".replace("RegularItalic", "Italic")
			for w in FIRA_WEIGHTS
			for s in ("", "Italic")
		),
		role="UI text, headings, slides, dashboards",
	),
	Family(
		slug="sans-math",
		name="Datacraft Sans Math",
		upstream_dir="fira-math",
		upstream_name="Fira Math",
		files=("FiraMath-Regular.otf",),
		role="OpenType MATH companion to Datacraft Sans",
		license_file="LICENSE",
	),
	Family(
		slug="mono",
		name="Datacraft Mono",
		upstream_dir="jetbrains-mono",
		upstream_name="JetBrains Mono",
		files=("JetBrainsMono[wght].ttf", "JetBrainsMono-Italic[wght].ttf"),
		role="Code, data tables, terminals",
		css_weight="100 800",
	),
)


def _out_stem(fam: Family, src: str) -> str:
	stem = Path(src).stem
	return stem.replace(fam.upstream_ps, fam.ps).replace("[wght]", "-Variable")


def _rename(font: TTFont, fam: Family) -> None:
	name = font["name"]
	ids = set(RENAMED_IDS)
	if "fvar" in font:
		for inst in font["fvar"].instances:
			ids.add(inst.subfamilyNameID)
			if inst.postscriptNameID not in (0xFFFF, None):
				ids.add(inst.postscriptNameID)
	if "STAT" in font:
		ids.update(r.nameID for r in name.names if r.nameID > 255)
	for rec in name.names:
		if rec.nameID not in ids:
			continue
		text = rec.toUnicode()
		for old, new in fam.renames():
			text = text.replace(old, new)
		rec.string = text
	upstream_version = name.getDebugName(5) or "unknown"
	name.setName(
		f"Version {VERSION}; Datacraft build of {fam.upstream_name} ({upstream_version})",
		5, 3, 1, 0x409,
	)
	ps = name.getDebugName(6)
	name.setName(f"{VERSION};{VENDOR};{ps}", 3, 3, 1, 0x409)
	copyright_ = name.getDebugName(0) or ""
	if "Datacraft" not in copyright_:
		name.setName(f"{copyright_} Modifications (renaming, vertical metrics) by Datacraft.", 0, 3, 1, 0x409)
	name.setName(
		f"{fam.name} is a renamed build of {fam.upstream_name} with Datacraft vertical metrics. {fam.role}.",
		10, 3, 1, 0x409,
	)
	# Drop legacy Mac-platform records so the Windows records above are authoritative.
	name.names = [r for r in name.names if r.platformID == 3]
	if "CFF " in font:
		cff = font["CFF "].cff
		new_ps = name.getDebugName(6)
		assert new_ps
		cff.fontNames = [new_ps]
		top = cff.topDictIndex[0]
		for attr in ("FullName", "FamilyName"):
			val = getattr(top, attr, None)
			if val:
				for old, new in fam.renames():
					val = val.replace(old, new)
				setattr(top, attr, val)
	font["OS/2"].achVendID = VENDOR


def _metrics(font: TTFont) -> None:
	upm = font["head"].unitsPerEm
	assert upm == 1000, f"metrics assume 1000 UPM, got {upm}"
	os2, hhea, head = font["OS/2"], font["hhea"], font["head"]
	os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = ASCENDER, DESCENDER, 0
	hhea.ascent, hhea.descent, hhea.lineGap = ASCENDER, DESCENDER, 0
	# Windows clips anything outside the win box, so it must cover the real bounds.
	os2.usWinAscent = max(os2.usWinAscent, head.yMax, ASCENDER)
	os2.usWinDescent = max(os2.usWinDescent, -head.yMin, -DESCENDER)
	os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS
	if os2.version < 4:
		os2.version = 4


def build_one(fam: Family, src: str) -> dict:
	path = UPSTREAM / fam.upstream_dir / src
	font = TTFont(path)
	glyphs_before = len(font.getGlyphOrder())
	had_math = "MATH" in font
	_rename(font, fam)
	_metrics(font)
	assert len(font.getGlyphOrder()) == glyphs_before
	assert ("MATH" in font) == had_math
	stem = _out_stem(fam, src)
	ext = path.suffix
	desktop = OUT_DESKTOP / fam.slug / f"{stem}{ext}"
	desktop.parent.mkdir(parents=True, exist_ok=True)
	font.save(desktop)
	web = OUT_WEB / f"{stem}.woff2"
	web.parent.mkdir(parents=True, exist_ok=True)
	font.flavor = "woff2"
	font.save(web)
	os2 = font["OS/2"]
	return {
		"family": fam.name,
		"slug": fam.slug,
		"file": web.name,
		"desktop": str(desktop.relative_to(ROOT)),
		"italic": "Italic" in src,
		"weight": fam.css_weight if "[wght]" in src else str(os2.usWeightClass),
		"x_height": os2.sxHeight,
		"cap_height": os2.sCapHeight,
		"math": had_math,
		"glyphs": glyphs_before,
		"woff2_bytes": web.stat().st_size,
	}


STATIC_WEIGHTS = {400: "Regular", 700: "Bold"}


def build_statics(fam: Family, src: str) -> list[Path]:
	"""Static Regular/Bold cuts of a variable source, for LaTeX and office apps."""
	from fontTools.varLib.instancer import instantiateVariableFont

	written = []
	italic = "Italic" in src
	for wght, label in STATIC_WEIGHTS.items():
		font = instantiateVariableFont(TTFont(UPSTREAM / fam.upstream_dir / src), {"wght": wght}, updateFontNames=True)
		assert "fvar" not in font
		_rename(font, fam)
		_metrics(font)
		style = f"{label}Italic".replace("RegularItalic", "Italic") if italic else label
		name = font["name"]
		name.removeNames(nameID=25)
		name.setName(f"{fam.ps}-{style}", 6, 3, 1, 0x409)
		name.setName(f"{VERSION};{VENDOR};{fam.ps}-{style}", 3, 3, 1, 0x409)
		out =OUT_DESKTOP / fam.slug / "static" / f"{fam.ps}-{style}.ttf"
		out.parent.mkdir(parents=True, exist_ok=True)
		font.save(out)
		written.append(out)
	return written


def write_css(faces: list[dict]) -> None:
	serif_x = next(f["x_height"] for f in faces if f["slug"] == "serif")
	sans_x = next(f["x_height"] for f in faces if f["slug"] == "sans")
	mono_x = next(f["x_height"] for f in faces if f["slug"] == "mono")
	lines = [
		"/* Datacraft fonts. Generated by build.py; edit the build, not this file. */",
		"",
	]
	for f in faces:
		lines += [
			"@font-face {",
			f'\tfont-family: "{f["family"]}";',
			f'\tsrc: url("../fonts/web/{f["file"]}") format("woff2");',
			f"\tfont-weight: {f['weight']};",
			f"\tfont-style: {'italic' if f['italic'] else 'normal'};",
			"\tfont-display: swap;",
			"}",
			"",
		]
	lines += [
		":root {",
		'\t--dc-serif: "Datacraft Serif", "STIX Two Text", Georgia, serif;',
		'\t--dc-sans: "Datacraft Sans", "Fira Sans", system-ui, sans-serif;',
		'\t--dc-mono: "Datacraft Mono", "JetBrains Mono", ui-monospace, monospace;',
		'\t--dc-math: "Datacraft Math", "STIX Two Math", math;',
		'\t--dc-sans-math: "Datacraft Sans Math", "Fira Math", math;',
		"\t/* Font-size factors that give code the x-height of the surrounding text. */",
		f"\t--dc-mono-in-serif: {serif_x / mono_x:.3f}em;",
		f"\t--dc-mono-in-sans: {sans_x / mono_x:.3f}em;",
		"}",
		"",
		"/* Opt-in contexts. Math follows the text family so glyph shapes match. */",
		"/* Lining figures in prose, so numbers in text match numbers in equations. */",
		".dc-prose { font-family: var(--dc-serif); font-variant-numeric: lining-nums proportional-nums; }",
		".dc-prose math { font-family: var(--dc-math); }",
		".dc-prose :is(code, kbd, samp, pre) { font-family: var(--dc-mono); font-size: var(--dc-mono-in-serif); }",
		".dc-ui { font-family: var(--dc-sans); font-variant-numeric: tabular-nums lining-nums; }",
		".dc-ui math { font-family: var(--dc-sans-math); }",
		".dc-ui :is(code, kbd, samp, pre) { font-family: var(--dc-mono); font-size: var(--dc-mono-in-sans); }",
		"/* Scale once: code nested inside pre keeps the pre size. */",
		":is(.dc-prose, .dc-ui) :is(code, kbd, samp, pre) :is(code, kbd, samp) { font-size: inherit; }",
		"",
	]
	css = ROOT / "css" / "datacraft.css"
	css.parent.mkdir(exist_ok=True)
	css.write_text("\n".join(lines))


def main() -> None:
	for d in (OUT_DESKTOP, OUT_WEB):
		shutil.rmtree(d, ignore_errors=True)
	faces: list[dict] = []
	for fam in FAMILIES:
		for src in fam.files:
			faces.append(build_one(fam, src))
			if "[wght]" in src:
				for p in build_statics(fam, src):
					print(f"{p.relative_to(ROOT)}  (static)")
		lic = UPSTREAM / fam.upstream_dir / fam.license_file
		shutil.copy(lic, OUT_DESKTOP / fam.slug / "OFL.txt")
	shutil.copy(UPSTREAM / "stix-two-text" / "OFL.txt", OUT_WEB / "OFL-STIX.txt")
	shutil.copy(UPSTREAM / "fira-sans" / "OFL.txt", OUT_WEB / "OFL-FiraSans.txt")
	shutil.copy(UPSTREAM / "fira-math" / "LICENSE", OUT_WEB / "OFL-FiraMath.txt")
	shutil.copy(UPSTREAM / "jetbrains-mono" / "OFL.txt", OUT_WEB / "OFL-JetBrainsMono.txt")
	write_css(faces)
	(ROOT / "fonts" / "manifest.json").write_text(json.dumps(faces, indent="\t") + "\n")
	assert len(faces) == sum(len(f.files) for f in FAMILIES)
	for f in faces:
		print(f"{f['file']:<42} {f['glyphs']:>5} glyphs  {f['woff2_bytes'] // 1024:>5} KiB{'  MATH' if f['math'] else ''}")


if __name__ == "__main__":
	main()
