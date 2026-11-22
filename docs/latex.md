# LaTeX and Pandoc

## Requirements

- LuaLaTeX (recommended) or XeLaTeX. pdfLaTeX can't load OpenType fonts.
- The `fontspec` and `unicode-math` packages, which are in every recent TeX Live and MiKTeX.
- The fonts and `datacraft.sty` installed ([install.md](install.md#latex)).

## The package

```latex
\usepackage{datacraft}          % Serif text, Datacraft Math
\usepackage[sans]{datacraft}    % Sans text, Datacraft Sans Math
```

| | Default | `sans` option |
|---|---|---|
| `\rmfamily` | Datacraft Serif | Datacraft Serif |
| `\sffamily` | Datacraft Sans | Datacraft Sans |
| `\ttfamily` | Datacraft Mono | Datacraft Mono |
| Body text | Serif | Sans |
| Math | Datacraft Math | Datacraft Sans Math |

Sans and Mono load with `Scale=MatchLowercase`, so their lowercase height matches the serif's at any size. Mono loads with `Ligatures=NoCommon`, which keeps `!=` and `->` as typed in listings.

Use the default for papers, theses and reports. Use `sans` for Beamer slides and posters, where Sans reads better from a distance:

```latex
\documentclass{beamer}
\usepackage[sans]{datacraft}
```

Load `datacraft` after any package that sets fonts. Don't load `amssymb`, `amsfonts`, `mathptmx` or other legacy math font packages next to it. `unicode-math` already provides every symbol they do, from the Datacraft math fonts, and the old packages can override it. `amsmath` is fine and recommended.

## Writing math

`unicode-math` changes a few habits:

- `\mathbb{E}`, `\mathcal{L}`, `\mathfrak{g}`, `\mathbf{x}` and `\symbf{x}` all work and come from the Datacraft math font.
- `\boldsymbol` is replaced by `\symbf` (bold italic for letters) or `\mathbf` (bold upright).
- You can type Unicode directly: `α ≤ β`, `∑`, `∫`, `ℝ`.
- For upright Greek constants, use `\upi` or `\symup{\pi}`.

Datacraft Math (STIX Two Math) covers the whole of Unicode math, including arrows, operators, and calligraphic, script, fraktur and double-struck alphabets. Datacraft Sans Math has fewer symbols. If a symbol prints as a blank box with the `sans` option, the font doesn't have it, and the log will say `Missing character`.

## Using the fonts without installing them

Set `\datacraftpath` before loading the package. It must end in a slash and point at `fonts/desktop/`:

```latex
\def\datacraftpath{/home/me/datacraft_fonts/fonts/desktop/}
\usepackage{datacraft}
```

Relative paths are resolved from the directory where you run `lualatex`. `latex/sample.tex` uses this approach and compiles as-is:

```sh
cd latex && lualatex sample.tex
```

## Without the package

If you'd rather write the fontspec setup yourself, the equivalent for installed fonts is:

```latex
\usepackage{fontspec}
\usepackage{unicode-math}
\setmainfont{Datacraft Serif}
\setsansfont{Datacraft Sans}[Scale=MatchLowercase]
\setmonofont{Datacraft Mono}[Scale=MatchLowercase]
\setmathfont{Datacraft Math}
```

Lookup by family name only works if you installed the static Serif and Mono files, not the variable ones.

## Pandoc

Pandoc's LaTeX template has variables for each font. Put them in the document's YAML header or a defaults file:

```yaml
---
mainfont: Datacraft Serif
sansfont: Datacraft Sans
monofont: Datacraft Mono
mathfont: Datacraft Math
sansfontoptions: [Scale=MatchLowercase]
monofontoptions: [Scale=MatchLowercase]
---
```

```sh
pandoc paper.md --pdf-engine=lualatex -o paper.pdf
```

Set `monofont` explicitly. Without it, Pandoc's template keeps Latin Modern Mono for code.

For HTML output, render the math as MathML so the web fonts apply:

```sh
pandoc paper.md --math-method=mathml -s -c css/datacraft.css -o paper.html
```

Then wrap the body in `.dc-prose`, or add `body { font-family: var(--dc-serif) } math { font-family: var(--dc-math) }` to your own CSS.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `The font "DatacraftSerif-Regular" cannot be found` | The fonts aren't installed where TeX looks, or `\datacraftpath` is wrong or lacks its trailing slash. LuaLaTeX caches its font list; run `luaotfload-tool --update` after installing fonts. |
| `fontspec error: cannot-use-pdftex` | You ran `pdflatex`. Use `lualatex` or `xelatex`. |
| Equations in Latin Modern | Something loaded after `datacraft` reset the math font, or a legacy math package is loaded. Load `datacraft` last. |
| Duplicate or wrong weights when loading by family name | Both the variable and static files are installed. Keep the static ones. |
| Very slow first run | LuaLaTeX builds its font name database once (`luaotfload \| db : Font names database not found`). Later runs are fast. |
