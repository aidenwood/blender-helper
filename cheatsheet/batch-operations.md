# Batch Operations — Ranked by Reliability

When you need to change the same property across many objects (very common with SVG-imported curves), here are the methods in order of how often they work first try, with the failure modes of each.

## 1. Right-click → Copy to Selected ★★★★★ (most reliable)

How:
1. Select all the target objects (orange outline).
2. Click the **source** object last so it becomes **active** (lighter outline).
3. In the Properties panel, right-click the property value field.
4. Choose **Copy to Selected**.

Works for: nearly all numeric properties, enums (dropdown values), booleans, and most data-block fields.

Failure modes:
- **Greyed out**: usually means only one object is selected, no active is set, or you right-clicked the label instead of the value field. See `troubleshooting/copy-to-selected-greyed-out.md`.
- Doesn't work on properties inside complex structs (some modifier internals).
- Mixed-type selection: copying a curve property to mesh objects is greyed out. Filter selection first.

## 2. Option+Enter on a typed value ★★★★ (fast when it works)

How:
1. Select all targets (+ active).
2. Click into the property value field on the active.
3. Type the new value.
4. Press `Option+Enter` instead of plain `Enter`.

Result: the value is set on every selected object.

Failure modes:
- Sometimes silently does nothing on Mac if focus is wrong. If a re-press of `Option+Enter` doesn't take, fall back to method 1.
- Three-button mouse emulation can intercept Option as a modifier — see `troubleshooting/option-click-not-working.md`.

## 3. Alt-drag a value across the field ★★★ (good for live tweaking)

How:
1. Select all + active.
2. Hover the property field.
3. Hold `Option` and drag left/right across the field.

The value scrubs and is applied to all selected. Good when you want to dial in a value visually.

## 4. Make Links → Object Data (`Cmd+L → Object Data`) ★★★ (powerful but blunt)

What it does: forces every selected object to **share the active's data block**. Not "copy the values" — they literally are the same data block.

Use when: you want 50 instances of the same geometry positioned differently (e.g. a bolt repeated across a chassis).

Avoid when: each object should keep its own geometry. For SVG-imported curves where each path is a different shape, this is **the wrong tool** — it would collapse all 50 shapes into 50 copies of one shape.

Reversible: `Object → Relations → Make Single User → Object & Data`.

## 5. Python script ★★★★★ (most reliable for many properties at once)

When the UI methods above feel slow:
- Setting 5 properties at once across 60 curves → script is faster than 5 × Copy to Selected.
- Conditional logic ("set extrude only on curves whose name starts with `outline_`") → only Python can do this.
- Setting properties on data inside data (e.g. material slot 0's base color) → much easier in Python than UI.

See `scripts/copy_active_curve_props_to_selected.py` for the template.

## 6. Drag-select across an Outliner column ★ (don't rely on this)

Not really a thing in modern Blender for curve props. The Outliner has limited inline editing — name, visibility toggles, and a few others. Skip and use one of the above.

## Decision flow

```
Need to change one property on many objects?
  ├─ Numeric / enum / bool, single property?   → Copy to Selected
  ├─ Numeric and want to visually dial in?     → Option+drag
  ├─ Multiple properties at once?              → Python (scripts/)
  ├─ Want them to share geometry, not copy?    → Make Links → Object Data
  └─ Need conditional logic?                   → Python (scripts/)
```
