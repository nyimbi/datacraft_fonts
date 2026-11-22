# Datacraft fonts

Five font families for equation-heavy writing: papers, blog posts and web app UIs. Text, math and code share one set of vertical metrics, so mixing them in a line doesn't shift the baseline or blow up the line height.

| Family | Use it for | Built from | Styles |
|---|---|---|---|
| Datacraft Serif | Body text in papers and long posts | STIX Two Text | variable 400 to 700, italic |
| Datacraft Math | Equations set with Datacraft Serif | STIX Two Math | Regular, OpenType MATH |
| Datacraft Sans | UI, headings, slides, dashboards | Fira Sans | 300, 400, 500, 600, 700, italics |
| Datacraft Sans Math | Equations set with Datacraft Sans | Fira Math 0.3.4 | Regular, OpenType MATH |
| Datacraft Mono | Code, data, terminals | JetBrains Mono | variable 100 to 800, italic |

Each math face is the companion of its text face. STIX Two Math was drawn to match STIX Two Text, and Fira Math to match Fira Sans, so an italic *x* in a formula is the same letter as an italic *x* in the sentence around it.

## What "Datacraft" changes

These are renamed, retuned builds of open-source fonts, not new outlines. The build does three things:

1. **Renames** every family-name record (and the CFF names in Sans Math). The upstream copyright and license records stay as they were. OFL 1.1 requires modified fonts to drop the upstream names.
2. **Unifies vertical metrics.** Every face gets ascender 900, descender -300, line gap 0 (per 1000 units), with `USE_TYPO_METRICS` set, so `line-height: normal` is 1.2 everywhere. The Windows clipping box is widened to each font's real bounds, so tall integrals and stacked fractions never clip.
3. **Cuts static instances** (Regular, Bold, Italic, Bold Italic) of the variable Serif and Mono for LaTeX and office apps, which handle variable fonts unevenly.

Glyph outlines, kerning, OpenType features and the MATH tables are untouched. The build asserts that glyph counts and MATH tables survive.

## Layout

```text
fonts/desktop/<family>/       TTF/OTF to install; static/ holds the Serif and Mono instances
fonts/web/                    WOFF2 for the web, plus the OFL licenses
fonts/manifest.json           per-face metadata (x-height, weight, size)
css/datacraft.css             @font-face rules and CSS variables
latex/datacraft.sty           fontspec and unicode-math setup
specimen/index.html           type specimen; open it in a browser
build.py, tests/              build and gate
sources/                      upstream fonts and licenses, see sources/INDEX.md
```

## Web

Copy `fonts/web/` and `css/datacraft.css`, keeping the `../fonts/web/` relative path, then opt in per region:

```html
<link rel="stylesheet" href="/css/datacraft.css">
<article class="dc-prose">...</article>   <!-- Serif, Math, scaled Mono -->
<div class="dc-ui">...</div>              <!-- Sans, Sans Math, tabular figures -->
```

Or use the variables directly: `--dc-serif`, `--dc-sans`, `--dc-mono`, `--dc-math`, `--dc-sans-math`. Inside `.dc-prose` and `.dc-ui`, inline `code` is scaled (`--dc-mono-in-serif` is 0.860em, `--dc-mono-in-sans` is 0.951em) so its x-height matches the surrounding text.

### Equations on the web

The math faces carry an OpenType MATH table, which browsers use to lay out native MathML. Chrome and Edge (109 and later), Firefox and Safari all support it. Render LaTeX to MathML and let the CSS pick the font:

- **Temml** converts LaTeX to MathML and is built for this setup.
- **KaTeX** with `output: "mathml"` works too. Its default HTML output uses KaTeX's own fonts and ignores Datacraft.
- **MathJax** draws with its own font data, so its CHTML and SVG output won't use Datacraft Math either.

Prose uses lining figures on purpose: numbers in a sentence should match numbers in the equation next to it.

## Desktop and LaTeX

Install the files under `fonts/desktop/` (on macOS, open them in Font Book). Then, with LuaLaTeX or XeLaTeX:

```latex
\usepackage{datacraft}          % Serif text with Datacraft Math
\usepackage[sans]{datacraft}    % Sans text with Datacraft Sans Math, for slides
```

To use the fonts without installing them, set the path first: `\def\datacraftpath{/abs/path/fonts/desktop/}`. Sans and Mono load with `Scale=MatchLowercase`, which matches their x-height to the serif. Mono ligatures are off in LaTeX, because `!=` drawn as `≠` in a code listing reads as math. On the web they stay on. Add `font-variant-ligatures: none` if you want them off there too. `latex/sample.tex` compiles as-is with `lualatex sample.tex`.

## Build

```sh
uv run build.py
uv run --with pytest --with fonttools --with brotli pytest -q tests
```

The tests check every built file: no upstream name in a family record, the shared metrics, a Windows box that covers the glyph bounds, license and copyright kept, and MATH tables present. A canary test runs the leak check against the untouched upstream fonts and expects it to fire.

## Known limits

- Fira Math is a 0.x release. It covers ordinary analysis, linear algebra and probability notation but fewer symbols than STIX Two Math. If a symbol is missing in Sans mode, switch that document to Serif and Datacraft Math.
- Datacraft Math is about 545 KiB as WOFF2. It is not subset, because subsetting a MATH font can drop the glyph variants and assemblies that stretchy delimiters need. Load it only on pages that have equations.
- Datacraft Serif comes in weights 400 to 700 only, which is what STIX Two Text offers. Use Datacraft Sans for light display text.

## License

SIL Open Font License 1.1, inherited from each upstream font. See `sources/INDEX.md` and the `OFL*.txt` files that ship with the fonts.
