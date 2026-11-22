# Installing Datacraft fonts

There are two ways in: install the fonts on your computer (for LaTeX, Typst, Word, matplotlib, your editor), or serve them from a website. You can do both.

## Get the files

Pick one:

- Download `datacraft-fonts-desktop-<version>.zip` (for your computer), `datacraft-fonts-web-<version>.zip` (for a website), or both from the [releases page](https://github.com/nyimbi/datacraft_fonts/releases).
- Or clone the repository: `git clone https://github.com/nyimbi/datacraft_fonts.git`. The built fonts are committed under `fonts/`, so you don't need to run the build.

## Desktop

### Which files to install

Serif and Mono each ship two forms with the same family name: one variable file per style (`*-Variable.ttf`) and four static files (`static/*.ttf`). **Install only one form per family**, or applications will list every style twice. The static files are the safer choice for LaTeX and Word. The variable files give you the in-between weights in apps that support them (recent Adobe apps, Figma, macOS apps).

The recommended desktop set is 18 files:

| Family | Install |
|---|---|
| Datacraft Serif | `fonts/desktop/serif/static/*.ttf` (4 files) |
| Datacraft Math | `fonts/desktop/math/DatacraftMath-Regular.ttf` |
| Datacraft Sans | `fonts/desktop/sans/*.ttf` (10 files) |
| Datacraft Sans Math | `fonts/desktop/sans-math/DatacraftSansMath-Regular.otf` |
| Datacraft Mono | `fonts/desktop/mono/static/*.ttf` (4 files) |

### macOS

Select the files in Finder, open them, and click **Install** in Font Book. Or from a terminal, at the repository root:

```sh
cp fonts/desktop/serif/static/*.ttf fonts/desktop/mono/static/*.ttf \
   fonts/desktop/sans/*.ttf fonts/desktop/math/*.ttf \
   fonts/desktop/sans-math/*.otf ~/Library/Fonts/
```

### Windows

Select the files in Explorer, right-click, and choose **Install** (just for you) or **Install for all users**. Install for all users if LaTeX or another program running under a different account needs to find them.

### Linux

```sh
mkdir -p ~/.local/share/fonts/datacraft
cp fonts/desktop/serif/static/*.ttf fonts/desktop/mono/static/*.ttf \
   fonts/desktop/sans/*.ttf fonts/desktop/math/*.ttf \
   fonts/desktop/sans-math/*.otf ~/.local/share/fonts/datacraft/
fc-cache -f
fc-list | grep -c Datacraft    # expect 18
```

### Check the install

Each family should appear once in your font menu, with the expected styles: Serif and Mono with four styles, Sans with ten, and each math font with one. If you see duplicates, you've installed both the variable and static files of a family; remove one set.

## LaTeX

Install the fonts as above, then put `latex/datacraft.sty` where TeX can find it:

```sh
dir="$(kpsewhich -var-value TEXMFHOME)/tex/latex/datacraft"
mkdir -p "$dir" && cp latex/datacraft.sty "$dir/"
```

On macOS, `TEXMFHOME` is usually `~/Library/texmf`; on Linux, `~/texmf`. Check it works with `kpsewhich datacraft.sty`. You need LuaLaTeX or XeLaTeX, since pdfLaTeX can't load OpenType fonts. Usage is in [latex.md](latex.md).

If you'd rather not install the fonts system-wide, skip the font install and point the package at the files instead (see [latex.md](latex.md#using-the-fonts-without-installing-them)).

## Website

Copy two directories into your site's static files, keeping them side by side:

```text
your-site/static/
  css/datacraft.css
  fonts/web/*.woff2
```

The stylesheet loads fonts from `../fonts/web/`, so that relative layout must stay intact. If your fonts live elsewhere, edit the `url(...)` paths in `datacraft.css`. Then link it:

```html
<link rel="stylesheet" href="/css/datacraft.css">
```

For a quick experiment you can load it straight from the jsDelivr CDN instead, pinned to a release tag:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/nyimbi/datacraft_fonts@v1.0.0/css/datacraft.css">
```

Self-host for production: you control caching, and the page doesn't depend on a third party. Next steps are in [web.md](web.md).

## Uninstalling

| Where | How |
|---|---|
| macOS | Remove the Datacraft files from `~/Library/Fonts/`, or delete the families in Font Book. |
| Windows | Settings, then Personalization, then Fonts. Select each Datacraft family and choose Uninstall. |
| Linux | `rm -r ~/.local/share/fonts/datacraft && fc-cache -f` |
| LaTeX | Delete the `datacraft` directory under `TEXMFHOME`. |
