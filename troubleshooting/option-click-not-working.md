# Option+Click / Option+Enter not working

You typed a value, hit `Option+Enter` expecting it to apply to all selected, and nothing happened — or it only changed the active. Or you `Option+Click`ed something and the wrong thing fired. Here's what's usually going on.

## 1. Three-button mouse emulation is intercepting Option

If `Edit → Preferences → Input → Emulate 3 Button Mouse` is **on**, Blender treats `Option+drag` as middle-mouse-drag (orbit). When you then try `Option+Click` on a value, Blender sees that as the start of an orbit gesture — and the click on the value field never registers as "apply to selected".

Two options:
- **Get a real 3-button mouse** and turn emulation off. `Option` becomes a clean modifier again.
- **Keep emulation, use Copy to Selected instead.** Right-click → Copy to Selected is 100% reliable and bypasses this entirely.

## 2. macOS owns the Option-key combo

System Settings → Keyboard → Keyboard Shortcuts → Mission Control / Spotlight / Input Sources can all claim Option-based combos. If any are enabled and conflict, macOS swallows the keypress before Blender sees it.

Check and disable any conflicts in those sections. After changes, restart Blender to be safe.

## 3. Focus is on the wrong editor

Blender's "apply to selected" reads which editor the cursor is hovering over. If you typed your value in the Properties panel but the cursor drifted onto the viewport before pressing `Option+Enter`, the keypress goes to the viewport's keymap (which has no "apply to selected" binding) and silently does nothing.

Fix: keep the cursor over the Properties panel from typing the value to pressing `Option+Enter`. Don't move the mouse during the operation.

## 4. The property doesn't support "apply to selected"

Some properties — particularly inside collections, modifier internals, and driven properties — don't support the "apply to selected" shortcut even though they accept Copy to Selected via right-click.

Fix: use right-click → Copy to Selected, or script it.

## 5. Karabiner / keyboard remappers

If you use Karabiner-Elements or similar to swap Option and Cmd globally, you'll need to either:
- Disable the remapping when Blender is the front app, or
- Adapt: press whichever physical key Blender now sees as Alt.

Check Karabiner's complex modifications list — even profiles you don't think are active can register on certain apps.

## 6. Sticky Keys / Slow Keys

macOS Accessibility settings can buffer modifier keys in unexpected ways. If you've recently enabled either, that's likely the cause.

System Settings → Accessibility → Keyboard → Sticky Keys / Slow Keys → off.

## Quick test to isolate the cause

Open a fresh Blender scene with the default cube:

1. `Shift+A` to add a second cube. Position it apart.
2. `A` to select both. Click cube 1 to make it active.
3. Properties → Object → Transform → Location X. Type `2`. Press `Option+Enter`.

Result interpretation:
- **Both cubes move to X=2** → Option+Enter is working; the issue with your real workflow is property-specific or focus-related.
- **Only the active cube moves** → focus or modifier-key issue. Try moving the mouse less, or check macOS shortcut conflicts.
- **Neither moves / something weird happens** → emulation or remapper is hijacking Option. Disable 3-button emulation and re-test.
