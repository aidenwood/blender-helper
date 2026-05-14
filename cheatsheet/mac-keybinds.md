# Mac-Specific Blender Keybinds

Most Blender tutorials are written for Windows. The translation is mostly "Ctrl → Cmd, Alt → Option", but there are real exceptions. This file lists the ones that bite you.

## The general rule (and where it breaks)

- **Cmd ≈ Ctrl** in Blender. `Cmd+S` saves, `Cmd+Z` undoes, `Cmd+J` joins, etc.
- **Option = Alt**. Used for "apply value to all selected" and various modifier-key tools.
- **Fn** may be needed to use F-keys as F-keys on MacBooks (otherwise they're media keys). Toggle in macOS System Settings → Keyboard.

## macOS shortcuts that override Blender's

When macOS owns a Cmd combo at the OS level, Blender never sees it. These are the common conflicts:

| Combo       | macOS does               | Blender wanted             | Workaround |
|-------------|--------------------------|----------------------------|------------|
| `Cmd+H`     | Hide Blender             | Hide selected object       | Hover viewport, press unmodified `H` |
| `Cmd+M`     | Minimize window          | Move (rarely bound)        | Use the unmodified `G` (grab) |
| `Cmd+Q`     | Quit Blender             | —                          | Just don't press it mid-session |
| `Cmd+W`     | Close window             | —                          | — |
| `Cmd+Tab`   | App switcher             | —                          | — |
| `Cmd+Space` | Spotlight                | —                          | — |

If a shortcut isn't working, suspect this list first.

## Confirmed working on macOS (Blender 5.x)

### Viewport navigation
- Orbit: middle-mouse-drag, OR `Option+drag` (with 3-button emulation on)
- Pan: `Shift+middle-mouse-drag`, OR `Shift+Option+drag`
- Zoom: scroll wheel, OR `Ctrl+Option+drag`
- Frame all: `Home`
- Frame selected: `.` (period on numpad, or top-row `.` with Emulate Numpad)

### Selection
- Select all / deselect all: `A` / `Option+A` (toggle: tap `A` twice)
- Box select: `B`
- Circle select: `C`
- Invert: `Ctrl+I`
- Add to selection: `Shift+click`
- Set active without changing selection: `Shift+click` an already-selected object

### Object ops
- Grab/move: `G`
- Rotate: `R`
- Scale: `S`
- Duplicate: `Shift+D`
- Delete: `X` (confirm with click or Enter)
- Hide selected: `H` (hover viewport, no modifier — see Cmd+H note above)
- Show hidden: `Option+H`
- Join (merge into active): `Cmd+J`
- Separate (in Edit Mode): `P`
- Parent: `Cmd+P`
- Clear parent: `Option+P`
- Apply menu (location/rotation/scale): `Cmd+A`
- Make Links menu: `Cmd+L`

### Modes
- Toggle Object/Edit: `Tab`
- Pie menu for all modes: `Ctrl+Tab`

### Save/file
- Save: `Cmd+S`
- Save As: `Shift+Cmd+S`
- Open: `Cmd+O`
- New: `Cmd+N`
- Undo: `Cmd+Z`
- Redo: `Shift+Cmd+Z`

### Property tricks
- Apply value to all selected: type new value → `Option+Enter` (instead of Enter). Sometimes flaky — see `troubleshooting/option-click-not-working.md`.
- Copy single property to selected: right-click the value → "Copy to Selected".
- Reset to default: right-click → "Reset to Default Value" (or backspace in the field).

## Required Preferences settings on Mac

Open `Edit → Preferences → Input`:

- **Emulate 3 Button Mouse** — on if you use a trackpad or 2-button mouse. Makes `Option+drag` orbit.
- **Emulate Numpad** — on if you're on a laptop without a numpad. Top-row numbers become numpad views (`1` front, `3` right, `7` top, `5` toggle ortho/persp, `0` camera).

Save startup: `File → Defaults → Save Startup File` so this persists across new files.

## Things that DON'T translate from Windows tutorials

- **Right-click context menu**: works the same, but with the Apple "right-click via Ctrl-click" macOS setting some users see lag. Use a real two-button mouse or set the trackpad to "Secondary click".
- **Middle-click on a property to reset to default**: works, but only with a real middle button — trackpad emulation doesn't reach this.
- **The N-panel** is the same key (`N`) — but the T-panel (toolbar) used to be `T`; in 5.x it still is, just confirming.
