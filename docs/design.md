# Design rationale

Datacraft is a selection and an integration, not a newly drawn typeface. No glyph outline was changed. What Datacraft decides is which open fonts belong together and how they share a page. This page explains those decisions and how firmly each one is supported.

## 1. Each math face comes from the same design as its text face

In a paper, the *x* in "let *x* be" and the *x* in an equation are the same symbol. If they're drawn by different designers, readers see two letters and wonder whether they mean different things. So each math face is the companion of its text face: STIX Two Math was drawn with STIX Two Text, and Fira Math with Fira Sans. That rules out popular pairings like Inter text with Latin Modern math, however good each looks alone.

It's also why both math faces carry an **OpenType MATH table**. The table records how equations are built: how far a subscript drops, how thick a fraction bar is, how a tall bracket is assembled from pieces. These are the parameters Knuth built into TeX, moved inside the font. Browsers, LuaLaTeX, XeLaTeX, Typst and Word all read it. A font without the table can supply symbols but can't build an equation.

## 2. Mixing faces never changes the line spacing

A browser sizes each line from the vertical metrics of every font used in it. Mix a serif, a math font and a code font with different metrics, and any line that holds a formula or a code span grows taller than its neighbours. That's the uneven spacing common on technical blogs.

All five families therefore get the same metrics: ascender 900, descender -300, line gap 0 (in a 1000-unit em), with the `USE_TYPO_METRICS` flag set so every platform reads the same numbers. `line-height: normal` is 1.2 in every face, and a line's height depends only on its tallest content, never on which font is present. The separate Windows clipping metrics are widened to each font's real glyph bounds, so tall integrals and stacked fractions never get cut off.

## 3. Faces are matched by lowercase height, not point size

How big text looks is set mostly by its x-height, the height of lowercase letters, not its nominal size. At the same nominal size, Datacraft Mono's x-height is 16% taller than Datacraft Serif's (550 against 473 units), so unscaled inline code shouts. The CSS shrinks code to 0.860em in serif text and 0.951em in sans text, and the LaTeX package uses `Scale=MatchLowercase`. This is a craft rule rather than a measured result, but it's the rule type designers work by.

## 4. Each family has one job

**Serif, from STIX Two Text.** STIX was commissioned by a consortium of scientific publishers for scientific publishing. It has the widest math coverage of any free font and is drawn to hold up at body sizes in print and on screen.

**Sans, from Fira Sans.** Fira was drawn for screens (it was Firefox OS's system font). Its large x-height and open letter shapes stay legible at UI sizes, and its ten styles give a UI room for hierarchy.

**Mono, from JetBrains Mono.** Characters that are easy to confuse in code are clearly distinct: `0O`, `1lI`, `rn` against `m`. Its x-height is tall for a monospace, which helps at small editor sizes.

Datacraft makes no claim that serif reads better than sans, or the reverse. The research on that is weak and contradictory. The split follows convention and context: serif for long reading, sans for interfaces.

## 5. Figures follow their job

**Prose uses lining figures,** digits at capital height. The *2* in a sentence should be the *2* in the equation beside it. Old-style figures, with their descending 3, 5, 7 and 9, are elegant in literary text and clash with math.

**UI uses tabular figures,** every digit the same width, so columns of numbers align and live-updating values don't make the layout jitter.

## 6. Mono ligatures depend on the medium

In an editor, `->` drawn as one arrow is a readability aid, and Datacraft Mono keeps its ligatures on the web and on the desktop. In a LaTeX document the same arrow inside a code listing reads as math notation, so the LaTeX package turns ligatures off.

## What this design does not do

Some questions belong to drawing a typeface, and Datacraft inherits its upstream fonts' answers to them.

Stroke contrast is one. STIX's fine hairlines are made for print and high-density screens, and on low-density screens Sans holds up better. Optical sizes are another: STIX Two Text has a single design for every size. The math faces do have script-size variants (the `ssty` feature), which math engines use for subscripts and superscripts automatically.

Nobody has tested Datacraft with readers, so it makes no claim about reading speed in dense notation.

The natural next step for an original Datacraft typeface would be a math-aware sans, since that's where free fonts are weakest: Fira Math is the only maintained option, and it's still pre-1.0.
