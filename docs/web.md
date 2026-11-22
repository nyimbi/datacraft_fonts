# Using Datacraft fonts on the web

This page assumes `css/datacraft.css` and `fonts/web/` are on your site ([install.md](install.md#website)).

## The stylesheet

`datacraft.css` defines 16 `@font-face` rules, five CSS variables and two opt-in classes. Nothing applies until you use a class or a variable, so loading it can't restyle an existing page by surprise.

### Classes

| Class | Text | Math (`<math>`) | Code (`code`, `kbd`, `samp`, `pre`) | Figures |
|---|---|---|---|---|
| `.dc-prose` | Datacraft Serif | Datacraft Math | Datacraft Mono at 0.860em | lining, proportional |
| `.dc-ui` | Datacraft Sans | Datacraft Sans Math | Datacraft Mono at 0.951em | lining, tabular |

```html
<article class="dc-prose">
	<p>For every <math><mi>t</mi><mo>&gt;</mo><mn>0</mn></math>, call <code>bound(t)</code>.</p>
</article>
<aside class="dc-ui">...</aside>
```

The code sizes give Datacraft Mono the same lowercase height as the text around it. Code nested inside `pre` keeps the `pre` size instead of shrinking twice.

### Variables

| Variable | Value |
|---|---|
| `--dc-serif` | `"Datacraft Serif", "STIX Two Text", Georgia, serif` |
| `--dc-sans` | `"Datacraft Sans", "Fira Sans", system-ui, sans-serif` |
| `--dc-mono` | `"Datacraft Mono", "JetBrains Mono", ui-monospace, monospace` |
| `--dc-math` | `"Datacraft Math", "STIX Two Math", math` |
| `--dc-sans-math` | `"Datacraft Sans Math", "Fira Math", math` |
| `--dc-mono-in-serif` | `0.860em` |
| `--dc-mono-in-sans` | `0.951em` |

The fallbacks are the upstream fonts, then a generic family, so a page still looks right if a WOFF2 file fails to load.

```css
body { font-family: var(--dc-sans); }
h1, h2, h3 { font-family: var(--dc-serif); font-weight: 600; }
```

### Weights and styles

| Family | `font-weight` | `font-style` |
|---|---|---|
| Datacraft Serif | any value from 400 to 700 (variable) | normal, italic |
| Datacraft Sans | 300, 400, 500, 600, 700 | normal, italic |
| Datacraft Mono | any value from 100 to 800 (variable) | normal, italic |
| Datacraft Math, Datacraft Sans Math | 400 | normal |

Don't apply `font-weight: bold` to a `<math>` element. The math fonts have one weight, so the browser would fake bold by smearing the outlines. Use `\mathbf` in your source, or `mathvariant="bold"` in MathML, which picks real bold math letters.

## Equations

The math fonts work through **MathML**, which Chrome and Edge (109 and later), Firefox and Safari render natively. The browser reads the font's OpenType MATH table for fraction rules, superscript shifts and stretchy delimiters. You write LaTeX, a converter turns it into MathML, and the stylesheet supplies the font.

### Temml (recommended)

[Temml](https://temml.org) converts LaTeX to MathML and nothing else, which is exactly this setup.

```js
import temml from "temml";

const html = temml.renderToString(String.raw`\int_0^1 x^2\,dx = \tfrac13`, { displayMode: true });
```

Temml also ships its own CSS files that set a math font. If you load one, load `datacraft.css` after it, or drop it: inside `.dc-prose` and `.dc-ui`, the Datacraft rules are more specific and win either way.

### KaTeX

KaTeX's default output is HTML drawn with KaTeX's own fonts, and it ignores Datacraft. Ask for MathML instead:

```js
katex.renderToString(tex, { output: "mathml", displayMode: true });
```

### MathJax

MathJax draws with its own font data in both its CHTML and SVG outputs, so Datacraft Math can't take part. If you use MathJax, the Datacraft text faces still apply to everything outside the equations.

### Markdown pipelines

- **Pandoc:** `pandoc post.md --math-method=mathml -s -o post.html`.
- **unified / rehype:** `rehype-katex` with `{ output: "mathml" }`.
- **markdown-it:** any math plugin that lets you supply the render function; call `temml.renderToString` from it.

Wrap the rendered post in `<article class="dc-prose">`.

### Checklist for a math page

1. Load `datacraft.css`.
2. Put the content inside `.dc-prose` or `.dc-ui`, or set `math { font-family: var(--dc-math); }` yourself.
3. Render LaTeX to MathML (`<math>` elements in the page, not `<span class="katex-html">`).
4. Check a tall expression, such as a fraction inside `\left( \right)`. If the parentheses stretch, the MATH table is in use.

## Frameworks

### Tailwind CSS v4

```css
@import "tailwindcss";
@import "./datacraft.css";

@theme {
	--font-serif: var(--dc-serif);
	--font-sans: var(--dc-sans);
	--font-mono: var(--dc-mono);
}
```

`font-serif`, `font-sans` and `font-mono` now use Datacraft. Add `tabular-nums` on tables.

### Next.js with `next/font/local`

`next/font` serves the files itself and generates the `@font-face` rules, so use it instead of `datacraft.css`:

```ts
import localFont from "next/font/local";

export const dcSerif = localFont({
	src: [
		{ path: "./fonts/DatacraftSerif-Variable.woff2", weight: "400 700", style: "normal" },
		{ path: "./fonts/DatacraftSerif-Italic-Variable.woff2", weight: "400 700", style: "italic" },
	],
	variable: "--dc-serif",
	adjustFontFallback: false,
});

export const dcMath = localFont({
	src: "./fonts/DatacraftMath-Regular.woff2",
	variable: "--dc-math",
	preload: false,
	adjustFontFallback: false,
});
```

Set `preload: false` on the math fonts so pages without equations don't download 545 KiB. Turn off `adjustFontFallback`, because the fonts already carry the metrics you want.

## Performance

| Family | Files | Total WOFF2 |
|---|---|---|
| Datacraft Serif | 2 | 324 KiB |
| Datacraft Math | 1 | 545 KiB |
| Datacraft Sans | 10 | 1.4 MiB (about 140 KiB per style) |
| Datacraft Sans Math | 1 | 93 KiB |
| Datacraft Mono | 2 | 143 KiB |

Browsers download only the faces a page actually uses, so a typical article page fetches Serif regular, Serif italic, Mono, and Math if it has equations.

- Every face uses `font-display: swap`, so text shows at once in the fallback font and swaps when the WOFF2 arrives.
- Preload the one or two faces used above the fold: `<link rel="preload" href="/fonts/web/DatacraftSerif-Variable.woff2" as="font" type="font/woff2" crossorigin>`.
- **Don't subset the math fonts.** Stretchy brackets and big operators are assembled from glyph variants that a character-based subsetter can't see, so it drops them.
- The text faces can be subset if you need to, for example `pyftsubset DatacraftSans-Regular.ttf --unicodes="U+0000-024F,U+0370-03FF,U+2000-206F" --flavor=woff2 --layout-features='*'`. Run it on the desktop TTF, not the WOFF2.

## Dark mode and rendering

The fonts don't need dark-mode changes. Light text on a dark background looks heavier than the same text dark on light, though. If body text feels bold in dark mode, Serif can't go lighter than 400, so set the body in Sans 300, or keep Serif and raise the line height slightly to open up the page.

Don't set `-webkit-font-smoothing: antialiased` on body text unless your design calls for thinner text. It makes STIX's hairlines very light on macOS.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Equations show in a different font | The renderer isn't producing MathML (KaTeX HTML or MathJax output), or the `<math>` element is outside `.dc-prose` and `.dc-ui`. |
| Fonts load locally but not in production | 404 on `fonts/web/*.woff2`: the CSS expects `../fonts/web/` relative to itself. Check the browser's network tab. |
| Fonts fail from a CDN or another domain | Fonts need CORS. The font server must send `Access-Control-Allow-Origin`. |
| Fake-bold equations | `font-weight` set on `<math>`. Remove it and use `\mathbf`. |
| `!=` shows as `≠` in code | Mono's coding ligatures. Add `font-variant-ligatures: none` on `code, pre`. |
