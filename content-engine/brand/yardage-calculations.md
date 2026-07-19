# Yardage Calculations — Plaza Park Interiors

Sourced from Morris's Google Drive calculation documents (Formulas spreadsheet,
Estimator Knowledge – Roman Shades and Draperies, Box Cushion Calculation,
Fabric Yardage Calculation Course, Yardage Calculation Formula, and related
files). These are the actual methodologies used in the Plaza Park Interiors
workroom. Use as the reference for any content that discusses yardage, quoting,
or fabric-order accuracy.

All rounding: **always CEILING to nearest 0.25 yard** for ordering. Never
round down; the extra is protection against dye-lot issues and cutting errors.

---

## Standard Seam Allowances and Hem Allowances

| Application | Allowance |
|---|---|
| Upholstery seams | 1/2" per seam |
| Drapery bottom hem | Double 4" (8" total) |
| Drapery side hem | Double 1.5" (3" per side) |
| Roman shade side hem | 3" total (1.5" per side) |
| Roman shade top/bottom | 20" total hem allowance |
| Foam — cut each side | 1/4" larger than finished dimension |

---

## Box Cushion Yardage

**Inputs:** W (width), L (length), T (thickness), FW (fabric width in inches),
PR (pattern repeat in inches, 0 if solid), N (number of cushions),
Seamed_Boxing (1 if seamed, 0 if cut from one piece).

### Step-by-step formulas

**A. Cushion Area (square inches):**
```
CA = 2 × (W × L + W × T + L × T)
```

**B. Convert to square yards:**
```
SY = CA / 1296
```

**C. Fabric yardage per cushion (solid or no repeat):**
```
FY = CEILING(SY / (FW / 36), 0.25)
```

**D. Pattern repeat adjustment:**
```
FY_adjusted = IF(PR > 0, FY + (PR / FW) × SY, FY)
```

**E. Seamed boxing adjustment (add 0.25 yd if boxing is seamed):**
```
FY_final = IF(Seamed_Boxing = 1, FY_adjusted + 0.25, FY_adjusted)
```

**F. Total yardage for all cushions:**
```
Total_Yardage = FY_final × N
```

### Railroaded vs. up-the-bolt

- **Railroaded fabric:** pattern runs horizontally along the bolt. Typically
  used when panel height exceeds 54" to avoid seams on the top face.
- **Up-the-bolt:** pattern runs vertically. Standard for most upholstery.
- Confirm orientation before finalizing cut order — it changes which dimension
  maps to the fabric width in the formula above.

### Welt/cord options

- **Self-welt:** cut from the same fabric as the top panel; include extra per
  the seam-allowance standard.
- **Contrast welt:** separate fabric order; track separately.
- **No welt:** no welt allowance needed.

---

## Roman Shades

### Inside Mount (IB)

```
Cut Width  = IB Width − 0.25" + 3" side hems  →  IB Width + 2.75"
Cut Length = IB Length + 20"
#Widths    = ROUNDUP(Cut Width / Fabric Width)
```

**Solid fabric:**
```
Total Yardage = CEILING(Cut Length / 36, 0.25) × #Widths
```

**Patterned fabric (vertical repeat VR):**
```
#Repeats   = ROUNDUP((IB Length + 20") / VR)
Cut Length = VR × #Repeats
Cut Yards  = CEILING(Cut Length / 36, 0.25)
Total      = #Widths × Cut Yards
```

### Outside Mount (OB)

```
Cut Width  = OB Width + 1" (size) + 3" side hems  →  OB Width + 4"
Cut Length = OB Height + 20"
#Widths    = ROUNDUP(Cut Width / Fabric Width)
Total      = CEILING(Cut Length / 36, 0.25) × #Widths
```

### Hobbled Roman Shade

```
Cut Length = (Finished Length × 2) + 20"
```
Apply same width and #widths formula as the mount type (IB or OB) above.

### Safety margin (alternative method)

Some calculators apply a 1.05 multiplier after the repeat/width math:
```
Total = (Cut Length / 36) × #Widths × 1.05
```
Use the repeat-adjusted method above when a vertical repeat is involved; the
1.05 approach is a fallback for solid or near-solid fabrics only.

### Worked example

Window: 72"W × 84"L, inside mount, 28" vertical repeat, 54" fabric.
```
Cut Width  = 72 + 2.75 = 74.75"
#Widths    = ROUNDUP(74.75 / 54) = 2
#Repeats   = ROUNDUP((84 + 20) / 28) = ROUNDUP(3.71) = 4
Cut Length = 28 × 4 = 112"
Cut Yards  = CEILING(112 / 36, 0.25) = CEILING(3.11) = 3.25
Total      = 3.25 × 2 = 6.5 yards
```

---

## Drapery Panels

### Inputs needed before calculating

- **Mount type:** inside or outside (sets the finished width baseline)
- **Fabric direction:** railroaded or up-the-bolt
- **Fabric width:** typically 54" (most upholstery/drapery goods) or 118"
  (wide-width sheers)
- **Fullness ratio:** how much fabric width per finished rod/track width
  (standard: 2.0–2.5× for pinch pleat; 1.8–2.0× for ripplefold)
- **Pattern repeat:** vertical repeat in inches (0 for solid or texture)
- **Number of panels**

### Finished width and cut width

```
Finished Width per Panel = (Rod/Track Width × Fullness Ratio) / # Panels
Cut Width per Panel      = Finished Width per Panel
                           + 3" per side hem (double 1.5")
```

### Cut length

```
Cut Length = Finished Length + 8" bottom hem (double 4") + 4" top hem/header
```

### Number of fabric widths per panel

```
#Widths = ROUNDUP(Cut Width per Panel / Fabric Width)
```

### Yardage per panel — solid fabric

```
Panel Yardage = CEILING(Cut Length / 36, 0.25) × #Widths
```

### Yardage per panel — patterned fabric

```
Cut Length (adjusted) = CEILING(Cut Length / VR, 1) × VR
Panel Yardage         = CEILING(Cut Length_adjusted / 36, 0.25) × #Widths
```

### Total project yardage

```
Total = Panel Yardage × # Panels
```

Add lining and interlining as separate line items; they do not share pattern
adjustments with the face fabric.

---

## Multi-Width Upholstery Pieces (Running-Foot Method)

For items like headboards, banquettes, or cornice boards where the piece is
wider than a single fabric width:

```
#Widths = ROUNDUP(Finished Width / Fabric Width)
Cut Length per width = Finished Height + seam allowances + any pattern repeat
Total Yardage = CEILING((Cut Length × #Widths) / 36, 0.25)
```

---

## Yardage for Multiple Pieces (Component Table)

When a project includes mixed components (drapery + cushions + trim), calculate
each component separately and sum:

| Component | Fabric Type | Quantity | Yardage Each | Subtotal |
|---|---|---|---|---|
| Drapery panels | Face fabric | 4 | — | — |
| Box cushions | COM | 2 | — | — |
| Trim (tape/cord) | Trim A | by linear ft | — | — |
| Lining | Standard lining | 4 | — | — |

Convert trim linear footage to fabric yardage only when trim is cut from yardage
goods (e.g., banding or welt from the face fabric). Pre-made trim (tape, cord,
fringe) is ordered in linear yards, not square yards.

---

## Pattern Repeat — Key Rules

1. **Always ask for the vertical repeat (VR) before finalizing the yardage order**
   — the swatch alone does not tell you.
2. A large repeat (12"+ VR) can add 15–30% to the yardage order; skip this
   and the client is short or the pattern doesn't match panel-to-panel.
3. For railroaded fabrics, the "repeat" that matters is the horizontal repeat
   across the bolt width — this governs seam placement, not cut length.
4. COM (customer's own material): confirm the repeat with your workroom
   **before the bolt ships**, not after it arrives. A yard short on a COM order
   means a project problem, not a yardage problem.

---

## Rounding Rule (applies to all calculations)

**Always round up to the nearest 0.25 yard (one quarter yard) for every
fabric component ordered.** Never round down. The ceiling function in the
formulas above enforces this.

Examples:
- 3.11 yd → 3.25 yd
- 6.78 yd → 7.00 yd
- 4.01 yd → 4.25 yd

---

## Notes for Content Use

- These formulas are the working methodology — refer to them in content as
  "we calculate it, we don't eyeball it" (the fullness-ratio video script line
  applies here too).
- Do not publish the full spreadsheet formulas in public-facing content; use
  them as the basis for explaining *why* the process matters and *what can go
  wrong* without the math.
- For educational content, the key message is: **the calculation happens before
  the order, not after**. Yardage errors that survive to fabrication can't be
  fixed without a remake.
- Reference the box-cushion yardage methodology in upholstery content as a
  concrete differentiator (area → square yards → ceiling-rounded to nearest
  0.25 → pattern and seam adjustments). This is in the blog post and the brand
  profile already.
