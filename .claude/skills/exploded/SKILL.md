---
name: exploded
description: Turns a furniture or product photo (or description) into a conceptual exploded-view assembly diagram that separates the piece into its component parts along an assembly axis, in the style of engineering/instruction-manual illustration. Use whenever the user says "/exploded", wants an "exploded view", "exploded diagram", "blow-apart view", "assembly diagram", or wants to show how a piece of furniture, casegood, seating frame, or building product goes together. Common in architecture, construction, interiors, manufacturing, and building-products marketing and technical presentations. Always ships with a conceptual-only disclaimer since it is not verified engineering documentation.
---

# /exploded — Exploded Assembly View

Produces a ready-to-run AI image-generation prompt (and, if an image
tool is available in this session, the rendered image itself) that
reimagines a source piece as a conceptual exploded-view diagram: the
components pulled apart along a shared axis so the assembly logic reads
at a glance.

## 1. Intake

Gather (ask only for what's missing — don't re-ask what the user already gave you):

- **Source**: a photo/render of the piece, or a written description (piece type, silhouette, proportions).
- **Piece type**: chair, sofa, case good, table, millwork unit, window-treatment hardware, building-product assembly, etc.
- **Known components**: frame, legs, seat deck, cushion core, upholstery/cover, hardware (bolts, cam locks, brackets, glides), joinery (mortise-and-tenon, dowel, dado, welded), fasteners, trim, drawer boxes — whatever actually applies. If the user doesn't know, infer a plausible breakdown from the piece type and say so is inferred.
- **Level of detail**: quick concept (5–8 parts) vs. detailed technical exploded view (all fasteners/hardware called out).
- **Label style**: none, numbered callouts only, or numbered + part-name leader lines.

## 2. Style recipe

Exploded views read well when the render commits to these choices:

- **Camera**: isometric or 3/4 axonometric, fixed angle, no perspective distortion.
- **Layout**: components separated along one consistent axis (usually vertical or the piece's natural assembly axis), largest/structural parts anchoring the composition, small hardware parts near their mating location.
- **Connectors**: thin dashed or solid guide lines linking each part back to its assembled position — the classic instruction-manual "flight path."
- **Background**: flat neutral (white or very light gray), no environment, no cast dramatic shadows — soft, even studio lighting only.
- **Line/surface treatment**: clean, slightly stylized CAD/technical-illustration rendering rather than photoreal grit — materials still legible (wood grain, metal, fabric) but simplified.
- **Labels** (if requested): small numbered circular tags with a thin leader line to each part; a simple legend/key beneath or beside the diagram.

## 3. Prompt template

Fill in brackets, drop any line that doesn't apply, then hand this to
the image tool:

```
Technical exploded-view illustration of [PIECE TYPE], isometric 3/4
angle, all components separated along a single vertical assembly axis
with thin [dashed/solid] guide lines connecting each part to its
assembled position. Components visible, ordered top to bottom /
outside to center: [LIST COMPONENTS, e.g. upholstered back cushion,
seat cushion, seat frame, corner blocks, front legs, rear legs,
stretcher, glides]. Render style: clean technical/engineering
illustration, simplified CAD-like surfaces, accurate proportions,
true-to-source materials and finish ([wood species / metal finish /
fabric]). Flat [white/light gray] background, soft even studio
lighting, no cast shadow drama, no environment. [If labeled: small
numbered circular callouts with thin leader lines to each part, plus a
compact numbered legend.] Composition centered, generous margin, high
resolution, no text watermark.
```

## 4. Execution

- If this session has an image-generation or image-editing tool/connector available (check via ToolSearch for something like image generation, editing, Gemini/Imagen, or a design canvas tool), use the source photo as a reference/edit input where the tool supports image-to-image, and run the prompt above.
- If no image tool is available, output the filled-in prompt as a clearly labeled code block the user can paste into their preferred image model (e.g. an image-capable chat app, Midjourney, or a design tool), and say so plainly.

## 5. Always append

End every delivered exploded view (image or prompt) with:

> ⚠️ **Conceptual visualization only.** This is an AI-generated
> illustration for ideation/presentation, not verified engineering
> documentation. Confirm actual component count, joinery, hardware,
> materials, and dimensions against real shop drawings, specifications,
> and construction details before using for manufacturing, quoting, or
> construction planning.
