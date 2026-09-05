---
name: sketch
description: Turns a furniture or product photo (or description) into a hand-drawn design concept sketch — pencil, ink, or marker rendering with a loose, early-concept feel. Use whenever the user says "/sketch", wants a "concept sketch", "hand-drawn rendering", "designer sketch", "marker rendering", or an early-stage/ideation-looking visual of furniture, interiors, or building products, as opposed to a polished or technical render. Common in architecture, construction, interiors, manufacturing, and building-products concept presentations. Always ships with a conceptual-only disclaimer.
---

# /sketch — Hand-Drawn Design Concept

Produces a ready-to-run AI image-generation prompt (and, if an image
tool is available in this session, the rendered image itself) that
reimagines a source piece as a hand-drawn concept sketch — the look of
an early design-development drawing, not a finished render.

## 1. Intake

Gather (ask only for what's missing):

- **Source**: photo/render of the piece, or a written description.
- **Piece type / context**: standalone product sketch, or the piece placed within a loose interior/room sketch.
- **Medium**: graphite pencil, ink line with wash, marker rendering (Copic-style, common in furniture/interiors concept work), or watercolor — ask if not specified; default to **marker rendering over ink line** since it's the most common professional furniture-concept medium.
- **Finish level**: quick thumbnail/gesture sketch (loose, a few lines, maybe multiple small studies on one sheet) vs. a single more resolved concept sketch with shading and material notes.
- **Annotations**: whether to include designer-style margin notes (material callouts, arrows, small color swatches) — a nice touch for concept presentations but optional.

## 2. Style recipe

- **Line quality**: visibly hand-drawn — slightly imperfect, confident linework, occasional construction/guide lines left visible (not erased to photoreal cleanliness).
- **Shading**: cross-hatching or loose marker strokes for form and shadow, not photographic gradients; leave some areas as open line (unrendered) the way a real concept sketch does.
- **Color**: limited palette — 2–4 marker tones plus the base ink/pencil line is typical; full photographic color grading defeats the purpose.
- **Paper**: visible sketch-paper or vellum texture/tone (warm white or cream), not a flat digital white.
- **Composition**: if "multiple studies," arrange 2–4 small loose variations/angles on one sheet, like a design-development page; if "single sketch," one larger centered study with room to breathe and optional margin notes.

## 3. Prompt template

```
Hand-drawn design concept sketch of [PIECE TYPE / PIECE WITHIN LOOSE
INTERIOR CONTEXT], [graphite pencil / ink line with marker rendering /
watercolor] on [cream sketch paper / vellum]. Loose, confident hand-
drawn linework with visible construction lines, cross-hatching or
loose marker strokes for shading and form, limited palette of [2-4
tones matching source material/color]. [Single resolved concept study,
centered, with room to breathe / 2-4 small loose thumbnail studies of
different angles arranged on one sheet]. [Include small margin notes:
material callouts, arrows, tiny color swatches, in a hand-lettered
style / no annotations]. Clearly an early-stage design sketch, not a
photoreal render — unrendered open areas are fine. No watermark, high
resolution scan quality.
```

## 4. Execution

- If this session has an image-generation or image-editing tool/connector available (check via ToolSearch for image generation, editing, Gemini/Imagen, or a design canvas tool), use the source photo as reference/edit input where supported and run the prompt above.
- Otherwise, output the filled-in prompt as a clearly labeled code block for the user to run in their preferred image tool, and say so plainly.

## 5. Always append

End every delivered sketch (image or prompt) with:

> ⚠️ **Conceptual visualization only.** This is an AI-generated
> concept sketch for early ideation or presentation, not a verified
> design or construction document. Confirm actual proportions,
> materials, and construction details against real drawings and
> specifications before proceeding to production.
