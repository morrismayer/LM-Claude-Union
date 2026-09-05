---
name: packshot
description: Upgrades a furniture or product photo into polished, catalog-ready product photography — clean studio background, professional lighting, e-commerce-ready retouching. Use whenever the user says "/packshot", wants a "packshot", "catalog image", "product photo cleanup", "hero shot", "studio shot", or wants a rough/phone photo of furniture, upholstery, hardware, or a building product turned into marketing-ready imagery. Common in architecture, construction, interiors, manufacturing, and building-products marketing collateral. Always ships with a note that this is a retouched/AI-assisted image, not a substitute for an accurate on-site or spec photo where fidelity matters.
---

# /packshot — Catalog-Ready Product Photography

Produces a ready-to-run AI image-generation/editing prompt (and, if an
image tool is available in this session, the rendered image itself)
that upgrades a source photo into clean, polished catalog/e-commerce
product photography — while keeping the actual piece, materials, and
proportions faithful to the source.

## 1. Intake

Gather (ask only for what's missing):

- **Source**: the actual photo to upgrade (required — packshot is a photo-to-photo upgrade, not a from-scratch generation; if the user has no photo, redirect them to /sketch or ask for a description-based render instead).
- **Background**: seamless white (classic e-commerce), seamless light gray, or a subtle gradient — default to seamless white unless the user's catalog uses a house style.
- **Framing/crop**: keep existing framing, or reframe to a standard catalog crop (centered, generous even margin, product filling ~70-80% of frame).
- **Angle count**: single hero shot, or note that multiple angles requires either multiple source photos or a follow-up generation per angle (this skill does not invent unseen sides of the piece from imagination — flag that risk if asked to show a hidden side).
- **Retouch scope**: background/lighting cleanup only (safest, most faithful) vs. also smoothing surface blemishes, wrinkles, dust, or stray background objects.

## 2. Style recipe

- **Background**: seamless, evenly lit studio backdrop (white, light gray, or specified), no visible seams, floor, or environment clutter.
- **Lighting**: soft, even, large-source studio lighting (softbox-style) — no harsh direct-flash shadows, no color cast; a soft, subtle contact/drop shadow or reflection under the product is fine and expected for e-commerce style.
- **Color/material fidelity**: preserve the actual color, finish, wood grain, fabric texture, and proportions of the source piece exactly — this is a lighting/background/retouch upgrade, not a redesign. Do not invent new materials, colors, or forms.
- **Sharpness/detail**: crisp focus across the product, clean edges against the backdrop, natural (not oversharpened/plastic) material rendering.
- **Crop/composition**: centered, generous even margin, standard catalog framing unless told otherwise.

## 3. Prompt template

```
Upgrade this product photo into polished catalog/e-commerce product
photography. Keep the exact product — same shape, proportions, color,
material, and finish as the source photo, no redesign. Replace
background with a seamless [white / light gray / specified] studio
backdrop, no visible seams or clutter. Relight with soft, even,
large-source studio lighting, no harsh shadows, no color cast; add a
subtle soft contact shadow/reflection beneath the product. [Clean up
surface blemishes, dust, wrinkles, and stray background objects /
background and lighting only, do not retouch the product surface].
Crop to standard centered catalog framing with even margin, product
filling roughly 70-80% of frame. Crisp focus, natural material
rendering, high resolution, no watermark.
```

## 4. Execution

- This skill needs an image-editing tool/connector that accepts an input photo (check via ToolSearch for an image editing/generation tool, e.g. Gemini/Imagen image editing or a similar connector). If one is available, pass the source photo plus the prompt above.
- If no such tool is available in this session, output the filled-in prompt as a clearly labeled code block for the user to run against the source photo in their preferred image-editing tool, and say so plainly.
- Never fabricate a photo-real result from a description alone and present it as a packshot "upgrade" of a real product — that only works starting from an actual source photo.

## 5. Always append

End every delivered packshot (image or prompt) with:

> ⚠️ **AI-retouched image.** Background, lighting, and minor retouching
> are AI-generated/assisted; verify color accuracy, material
> representation, and any hidden angles or details against the actual
> product before using in a catalog, spec sheet, or contract document
> where exact fidelity matters.
