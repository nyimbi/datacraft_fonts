# Typst, Word, matplotlib and editors

All of these use the installed desktop fonts ([install.md](install.md#desktop)).

## Typst

Typst reads OpenType MATH tables, so the math fonts work fully:

```typst
#set text(font: "Datacraft Serif", size: 11pt)
#show math.equation: set text(font: "Datacraft Math")
#show raw: set text(font: "Datacraft Mono")

For $t > 0$,
$ Pr[S_n - EE S_n >= t] <= exp(-(2 t^2) / (sum_(i=1)^n (b_i - a_i)^2)) $
```

For slides, swap in `"Datacraft Sans"` and `"Datacraft Sans Math"`. To compile without installing the fonts, pass their directory: `typst compile --font-path path/to/fonts doc.typ`. Typst finds fonts in subdirectories, but put only one of the variable and static files of a family on that path.

<!-- docs-qa: ignore SLOP005 (product names) -->
## Microsoft Word and PowerPoint

1. Install the fonts, then restart Word.
2. Set the body text font to Datacraft Serif (or Sans) in the Normal style: Home, then Styles, right-click **Normal**, then Modify.
3. Set the equation font: insert an equation, open the **Equation** tab, click the small arrow in the corner of the **Tools** group to open Equation Options, and choose **Datacraft Math** under "Default font for math regions". Word lists only fonts that have an OpenType MATH table there, so both Datacraft math fonts appear and the text faces don't.

Word stores the font name in the document. Someone opening the file without Datacraft installed gets a substitute font. Export to PDF to share a fixed layout, since Word embeds the fonts and the OFL permits that.

These Word steps were written from Word's documented options and haven't been tested against the current release.

## matplotlib

matplotlib doesn't use OpenType MATH tables. Its `mathtext` engine builds equations from ordinary fonts and its own layout rules, so you can get matching text but only an approximate match for math. Register the fonts first:

```python
from pathlib import Path
from matplotlib import font_manager

for p in Path("fonts/desktop").rglob("*.[ot]tf"):
	if "Variable" not in p.name:
		font_manager.fontManager.addfont(str(p))
```

### Serif figures, for papers

```python
import matplotlib.pyplot as plt

plt.rcParams.update({
	"font.family": "Datacraft Serif",
	"mathtext.fontset": "stix",
})
```

`stix` is matplotlib's bundled STIX General, the predecessor of STIX Two, so equations in figures match Datacraft Math closely without being identical.

### Sans figures, for dashboards and slides

```python
plt.rcParams.update({
	"font.family": "Datacraft Sans",
	"mathtext.fontset": "custom",
	"mathtext.rm": "Datacraft Sans",
	"mathtext.it": "Datacraft Sans:italic",
	"mathtext.bf": "Datacraft Sans:bold",
	"mathtext.sf": "Datacraft Sans",
	"mathtext.tt": "Datacraft Mono",
	"mathtext.cal": "Datacraft Sans:italic",
	"mathtext.fallback": "stixsans",
})
```

Letters and digits in equations then come from Datacraft Sans, and symbols the font lacks (∑, √) fall back to STIX Sans. `\mathcal{L}` draws as an italic Sans L, because mathtext can't reach the script letters inside the math font. If you need real calligraphic letters, leave `mathtext.cal` at its default.

Save figures as PDF or SVG for papers. matplotlib embeds a subset of each font in the PDF. For SVG, set `plt.rcParams["svg.fonttype"] = "none"` to keep text as text, so the web page's Datacraft fonts render it.

## Code editors and terminals

Use **Datacraft Mono**. It has coding ligatures (`->`, `!=`, `<=`), which most editors render only when asked.

- **VS Code:** `"editor.fontFamily": "Datacraft Mono"`, `"editor.fontLigatures": true`, and the same for `terminal.integrated.fontFamily`.
- **JetBrains IDEs:** Settings, then Editor, then Font; choose Datacraft Mono and tick **Enable ligatures**.
- **Terminals** (iTerm2, WezTerm, Ghostty, Windows Terminal): choose Datacraft Mono in the profile's font setting.

With the variable file installed you can choose any weight from 100 to 800. The static install gives Regular and Bold.

## Jupyter

Notebook and JupyterLab output is HTML, and Jupyter renders `$...$` with MathJax, which uses its own fonts. To use Datacraft in exported HTML, export with Pandoc ([latex.md](latex.md#pandoc)), or include `datacraft.css` in the export template and render math to MathML.
