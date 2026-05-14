# Active vs Selected — and why the difference matters

This is the single most-tripped-up concept for new Blender users on Mac (and everyone else). Getting it right unlocks Copy to Selected, Make Links, parenting, snapping, and half the other "do this from a source" operators.

## The two states

### Selected
- ANY object with an **orange outline** in the viewport.
- Multiple objects can be selected at once.
- In the outliner, selected rows have a subtle background highlight.
- Most operators (move, rotate, scale, delete, hide) act on ALL selected objects.

### Active
- The **most recently clicked / interacted** object.
- Has a **lighter outline** — usually pale yellow or white, depending on theme.
- **Only ONE** object is active at a time.
- The Properties panel always shows the **active's** data.
- Operators that need a "source" — Copy to Selected, Make Links, Parent To, Snap Selection to Active — use the active.

You can have selected objects without an active (rare, after some deselect operations). You can have an active that's also selected (the normal case).

## Visual check

In the viewport:
- Pale / lighter outline = **active**.
- Plain orange outline = **selected** (but not active).
- No outline = not selected.

In the outliner:
- The row icon colour: a **lighter highlight** on the active row.
- Plain orange icon next to the object name on other selected rows.

If the Properties panel is showing the wrong object's data, you're looking at what's active. Click the one you want and watch the panel switch.

## Why it matters — Copy to Selected

The operator is literally:

> Copy this property's value FROM the active TO every other selected object.

So:
- 0 selected + 0 active → menu greyed out.
- 1 object both selected and active → no targets → greyed out.
- 5 selected, 1 of which is active → copies from active to 4 others. Works.

## How to manage active intentionally

| You want                                          | Do this |
|---------------------------------------------------|---------|
| Select N objects, then set one as the source      | Box-select all N (`B` drag). `Shift+click` the source last — it becomes active without deselecting others. |
| Add to selection, set as active                   | `Shift+click` an unselected object. Adds it to selection AND makes it active. |
| Toggle one off without disrupting active          | `Ctrl+click` — toggles selection on that object. |
| Make an already-selected object active            | `Shift+click` it. (Toggles off and back on, but lands as active.) |
| Make active without changing selection at all     | In recent Blender: just click without modifier — but this deselects others. Workaround: `Shift+click` the active off, then `Shift+click` it back on. |

## Common confusing situation

**"I selected three curves and Copy to Selected is greyed out."**

Almost certainly: you box-selected three curves but the active is still some _other_ object from before (maybe the parent Empty), OR the active is one of the three but you only see one orange outline because the viewport angle is hiding the others.

Fix routine:
1. `Option+A` to deselect everything.
2. Click target curve 1.
3. `Shift+click` target curve 2.
4. `Shift+click` target curve 3.
5. `Shift+click` the SOURCE curve last.

Now selection has four orange outlines, source has the pale outline = active. Right-click property → Copy to Selected.

## In Python

For when you script it:

```python
import bpy

active = bpy.context.active_object             # one object or None
selected = bpy.context.selected_objects        # list, includes the active

# Set active programmatically:
bpy.context.view_layer.objects.active = some_object

# Select / deselect programmatically:
some_object.select_set(True)
some_object.select_set(False)
```

`selected_objects` includes the active (because the active is also selected, almost always). If you want "selected but not active":

```python
targets = [o for o in selected if o is not active]
```

That's exactly what `scripts/copy_active_curve_props_to_selected.py` does.
