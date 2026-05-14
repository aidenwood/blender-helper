# Optional: Blender MCP integration

This is a "later" upgrade — not needed to use this project. Without MCP, Claude Code helps by giving you UI steps and scripts you paste into Blender. With MCP, Claude Code can drive Blender directly: query the scene, run operators, set properties.

## Recommended project

**blender-mcp** by ahujasid:
https://github.com/ahujasid/blender-mcp

Check the project README before installing — it's the most actively maintained Blender MCP server. Setup steps below are accurate as of writing but always defer to the upstream README if they conflict.

## Install (rough outline)

1. **Install the Blender addon side**:
   - Download the `addon.py` (or the latest release `.zip`) from the GitHub repo.
   - In Blender: `Edit → Preferences → Add-ons → Install from Disk` → select the file → enable the checkbox.
   - The addon adds a panel in the 3D viewport N-panel (press `N`, look for the "BlenderMCP" tab).

2. **Start the MCP server inside Blender**:
   - Open the N-panel → BlenderMCP tab.
   - Click "Connect to Claude" (or equivalent — the button name may shift between versions).
   - Leave Blender running. The server listens for MCP connections.

3. **Add the MCP server to Claude Code**:
   ```bash
   claude mcp add blender -- uvx blender-mcp
   ```
   Or, if the project's README specifies a different command, use theirs. The `--` separator passes everything after it as the launch command for the server.

4. **Restart Claude Code**, then run `/mcp` to verify. You should see `blender` listed with status `connected`.

## What it unlocks

When the server is up, Claude can:
- Query the scene state — what's selected, what's active, what mode, what objects exist.
- Run operators — select objects, set properties, switch modes.
- Read and write properties on objects, materials, modifiers.
- Render via Cycles/Eevee if exposed by the addon.

This means I can say "set extrude to 0.05 on all the curves in the Logo collection" and Claude can do it directly, then screenshot the result — no copy-paste required.

## When to skip this

- If you're learning Blender, **skip it for now**. Pasting scripts into the Scripting workspace teaches you what Blender's actually doing.
- If you don't have time to debug the addon connection, **skip it**. The pasted-script workflow is 95% as efficient for everything in `scripts/`.

Come back to this once the manual workflow feels limiting.

## Security note

The MCP server exposes scripting capability to Claude. Treat it like any code-execution tool — don't run untrusted prompts against it. Default to using it with your own files only.
