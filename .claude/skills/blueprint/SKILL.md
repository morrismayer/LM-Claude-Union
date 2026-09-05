---
name: blueprint
description: Turns a furniture or product photo (or description) into a clean technical-drawing-style presentation — orthographic elevation/plan/section views with dimension lines and a drafting aesthetic. Use whenever the user says "/blueprint", wants a "blueprint", "technical drawing", "shop drawing look", "schematic", "line drawing", "CAD-style view", or "spec-sheet style" image of furniture, casegoods, millwork, window treatments, or building products. Common in architecture, construction, interiors, manufacturing, and building-products presentations. Always ships with a conceptual-only disclaimer since it is not a substitute for verified shop or construction drawings.
---

# /blueprint — Technical Blueprint Presentation

Produces a ready-to-run AI image-generation prompt (and, if an image
tool is available in this session, the rendered image itself) that
reimagines a source piece as a clean technical/drafting-style
presentation, in the spirit of a shop drawing or spec sheet — not a
photoreal render.

## 1. Intake

Gather (ask only for what's missing):

- **Source**: photo/render of the piece, or a written description.
- **Piece type**: chair, sofa, casegood, table, drapery hardware, millwork, window treatment, building-product component, etc.
- **View(s) wanted**: front elevation, side elevation, plan (top) view, section/cutaway, or a combined multi-view sheet (most common: front + side + plan, three-view).
- **Palette**: classic blueprint (white/light linework on deep blue), or modern drafting (black linework on white) — ask if not specified; default to modern white-background/black-line if the piece will sit in marketing collateral, classic blue if it's meant to read as archival/technical.
- **Dimensioning**: whether to include dimension lines/arrows and (if known) real measurements, or leave dimension lines present but unlabeled as a stylistic cue only.

## 2. Style recipe

- **Projection**: true orthographic (no perspective) for each view; if multiple views requested, arrange them in a standard drafting layout (plan above, elevations beside/below, aligned on shared axes).
- **Linework**: uniform-weight clean line drawing, minimal or no shading/fill — hatching only where useful to indicate material or a section cut.
- **Dimension lines**: thin extension/dimension lines with arrowheads and small tick marks; if real dimensions are known, label them; otherwise indicate lines without numbers or note "dimensions indicative only."
- **Title block**: small corner title block with piece name, view name(s), and scale notation (e.g. "SCALE 1:10" or "NTS" if not to scale) — purely stylistic, not a real stamped drawing.
- **Background**: flat, uncluttered (deep blue for classic blueprint, or white/very light gray for modern drafting); no photographic texture or environment.
- **Color**: one or two tones only (background + linework color), no photographic color grading.

## 3. Prompt template

```
Technical blueprint-style line drawing of [PIECE TYPE], orthographic
projection, [front elevation / side elevation / plan view / combined
three-view layout: plan, front elevation, side elevation aligned in
standard drafting arrangement]. Clean uniform-weight linework, minimal
shading, [material hatching on section cut if applicable]. Include thin
dimension lines with arrowheads [labeled with approximate dimensions:
LIST / left unlabeled, indicative only]. Small corner title block with
piece name and scale notation. Palette: [deep blue background with
white linework, classic blueprint style / white background with black
linework, modern drafting style]. No photographic texture, no
perspective, no environment, high resolution, no watermark.
```

## 4. Execution

- If this session has an image-generation or image-editing tool/connector available (check via ToolSearch for image generation, editing, Gemini/Imagen, or a design canvas tool), use the source photo as reference/edit input where supported and run the prompt above.
- Otherwise, output the filled-in prompt as a clearly labeled code block for the user to run in their preferred image tool, and say so plainly.

## 5. Always append

End every delivered blueprint (image or prompt) with:

> ⚠️ **Conceptual visualization only.** This is an AI-generated
> technical-style illustration for presentation, not a certified or
> to-scale shop/construction drawing. Any dimensions shown are
> indicative, not measured. Verify actual dimensions, joinery, and
> construction details against real drawings and specifications before
> using for fabrication or construction.
