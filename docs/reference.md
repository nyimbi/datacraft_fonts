# Reference

Measurements are in font units of a 1000-unit em. `fonts/manifest.json` has the same data in machine-readable form.

## Faces

| Web file | Weight | Style | x-height | Cap height | Glyphs | WOFF2 |
|---|---|---|---|---|---|---|
| `DatacraftSerif-Variable.woff2` | 400 to 700 | normal | 473 | 657 | 2221 | 154 KiB |
| `DatacraftSerif-Italic-Variable.woff2` | 400 to 700 | italic | 467 | 657 | 2238 | 170 KiB |
| `DatacraftMath-Regular.woff2` | 400 | normal | 473 | 657 | 6760 | 545 KiB |
| `DatacraftSans-Light.woff2` | 300 | normal | 523 | 685 | 2708 | 133 KiB |
| `DatacraftSans-LightItalic.woff2` | 300 | italic | 523 | 685 | 2707 | 140 KiB |
| `DatacraftSans-Regular.woff2` | 400 | normal | 527 | 689 | 2708 | 134 KiB |
| `DatacraftSans-Italic.woff2` | 400 | italic | 527 | 689 | 2707 | 142 KiB |
| `DatacraftSans-Medium.woff2` | 500 | normal | 529 | 691 | 2708 | 137 KiB |
| `DatacraftSans-MediumItalic.woff2` | 500 | italic | 529 | 691 | 2707 | 145 KiB |
| `DatacraftSans-SemiBold.woff2` | 600 | normal | 530 | 692 | 2708 | 143 KiB |
| `DatacraftSans-SemiBoldItalic.woff2` | 600 | italic | 530 | 692 | 2707 | 152 KiB |
| `DatacraftSans-Bold.woff2` | 700 | normal | 531 | 693 | 2708 | 143 KiB |
| `DatacraftSans-BoldItalic.woff2` | 700 | italic | 531 | 693 | 2707 | 152 KiB |
| `DatacraftSansMath-Regular.woff2` | 400 | normal | 527 | 689 | 2094 | 93 KiB |
| `DatacraftMono-Variable.woff2` | 100 to 800 | normal | 550 | 730 | 1179 | 69 KiB |
| `DatacraftMono-Italic-Variable.woff2` | 100 to 800 | italic | 550 | 730 | 1179 | 74 KiB |

## Desktop files

| Directory | Files | Format |
|---|---|---|
| `fonts/desktop/serif/` | `DatacraftSerif-Variable.ttf`, `DatacraftSerif-Italic-Variable.ttf` | TrueType, variable `wght` |
| `fonts/desktop/serif/static/` | `DatacraftSerif-{Regular,Italic,Bold,BoldItalic}.ttf` | TrueType |
| `fonts/desktop/math/` | `DatacraftMath-Regular.ttf` | TrueType with MATH |
| `fonts/desktop/sans/` | `DatacraftSans-{Light,Regular,Medium,SemiBold,Bold}{,Italic}.ttf` | TrueType |
| `fonts/desktop/sans-math/` | `DatacraftSansMath-Regular.otf` | CFF with MATH |
| `fonts/desktop/mono/` | `DatacraftMono-Variable.ttf`, `DatacraftMono-Italic-Variable.ttf` | TrueType, variable `wght` |
| `fonts/desktop/mono/static/` | `DatacraftMono-{Regular,Italic,Bold,BoldItalic}.ttf` | TrueType |

The regular Sans file is `DatacraftSans-Regular.ttf` and its italic is `DatacraftSans-Italic.ttf`, not `RegularItalic`.

## Vertical metrics (every face)

| Field | Value |
|---|---|
| `OS/2.sTypoAscender` / `hhea.ascent` | 900 |
| `OS/2.sTypoDescender` / `hhea.descent` | -300 |
| `OS/2.sTypoLineGap` / `hhea.lineGap` | 0 |
| `OS/2.fsSelection` bit 7 (`USE_TYPO_METRICS`) | set |
| `OS/2.usWinAscent` / `usWinDescent` | at least the font's `head.yMax` / `-head.yMin` |
| Default line height | 1.2 |

## Font names

| Family (name ID 1/16) | PostScript names | Vendor ID |
|---|---|---|
| Datacraft Serif | `DatacraftSerif-Regular`, `-Italic`, `-Bold`, `-BoldItalic` (static) | `DTCR` |
| Datacraft Math | `DatacraftMath-Regular` | `DTCR` |
| Datacraft Sans | `DatacraftSans-Light` through `DatacraftSans-BoldItalic` | `DTCR` |
| Datacraft Sans Math | `DatacraftSansMath-Regular` | `DTCR` |
| Datacraft Mono | `DatacraftMono-Regular`, `-Italic`, `-Bold`, `-BoldItalic` (static) | `DTCR` |

Name ID 5 reads `Version 1.000; Datacraft build of <upstream> (<upstream version>)`, so any file tells you exactly what it was built from.

## OpenType features

The upstream features are kept unchanged. Read from the files' `GSUB` tables:

| Feature | Serif | Sans | Mono | Math | Sans Math | Use |
|---|---|---|---|---|---|---|
| `pnum` | yes | yes | | | yes | Proportional figures |
| `tnum` | default | yes | default | | | Tabular figures |
| `lnum` | default | yes | default | | | Lining figures |
| `onum` | yes | yes | | | | Old-style figures |
| `smcp`, `c2sc` | yes | yes | | | | Small capitals |
| `frac`, `sups`, `subs` | yes | yes | yes | | | Fractions, superior and inferior figures |
| `liga` | yes | yes | | | yes | Standard ligatures (fi, fl) |
| `calt` | | yes | yes | | | Contextual alternates; Mono's coding ligatures (`->`, `!=`) |
| `zero` | | yes | yes | | | Slashed zero |
| `ssty` | | | | yes | yes | Script-size glyphs, applied by math engines |
| `ss01` and up | | `ss01` to `ss04` | | `ss01` to `ss20` | `ss01` to `ss03` | Stylistic sets |

"Default" means the font's normal digits already have that form, so the feature has nothing to do. Serif and Mono digits are lining and tabular by default. Sans digits are lining and proportional. That's why `.dc-prose` turns on `pnum` and `.dc-ui` turns on `tnum`.

Datacraft Math's stylistic sets switch in alternate letterforms. The STIX Two documentation lists what each set does. Check what a file supports with:

```sh
python3 -c "import sys; from fontTools.ttLib import TTFont; print(sorted({r.FeatureTag for r in TTFont(sys.argv[1])['GSUB'].table.FeatureList.FeatureRecord}))" <file>
```

## Repository layout

```text
build.py                 build script
tests/test_fonts.py      gate on the built fonts
sources/upstream/        upstream fonts and their licenses
sources/INDEX.md         provenance of every upstream file
fonts/desktop/           TTF/OTF to install
fonts/web/               WOFF2 and licenses for the web
fonts/manifest.json      per-face metadata
css/datacraft.css        generated stylesheet
latex/datacraft.sty      LaTeX package
latex/sample.tex         LaTeX example
specimen/index.html      type specimen
docs/                    this documentation
```
