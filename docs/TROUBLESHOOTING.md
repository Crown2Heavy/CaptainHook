# Troubleshooting Log - CaptainHook

## 🛠️ Builder & Compilation Issues

### 1. PyInstaller Module Loading Failure
*   **Problem:** After compilation, the bot responds to `$help` but doesn't load modules like `screenshot` or `shell`.
*   **Error:** `Failed to load module ...: No module named 'src.client.modules'` in terminal.
*   **Root Cause:** PyInstaller's analysis doesn't automatically find modules loaded via dynamic strings (e.g., `load_extension`).
*   **Fix:** 
    *   Updated `src/builder/main.py` to explicitly include all selected modules via `--hidden-import`.
    *   Added `--paths` to point to the `build_staging` directory so PyInstaller can resolve the `src.client` package.
    *   Implemented fallback loading in `src/client/main.py` to try `modules.{name}` if `src.client.modules.{name}` fails.

### 2. Shell Copy-Paste "Command Not Found"
*   **Problem:** Copying the build command from the CLI output fails with `bash: --hidden-import... command not found`.
*   **Root Cause:** The CLI UI was wrapping the command onto multiple lines or including decorative border characters (`│`). The shell interpreted the second line as a new, non-existent command.
*   **Fix:** Updated `src/builder/main.py` to print the final command as a single, clean line without borders or forced line breaks.

### 3. Missing Session Channels
*   **Problem:** Bot comes online but no Discord channel is created.
*   **Root Cause:** 
    1.  Invalid `Config.GUILD_ID` (placeholders not replaced).
    2.  Bot lacks `Manage Channels` permission.
    3.  `on_ready` failing silently.
*   **Fix:** Added diagnostic logging to `main.py` and a built-in `$p` (ping) command that works even if all modules fail to load.

## 🐍 Python & Environment

### 1. Docker Wine Dependency Errors
*   **Problem:** `Package 'libportaudio-dev' has no installation candidate`.
*   **Fix:** Use `portaudio19-dev` on Debian Trixie/Sid based images.

---
*Last Updated: 2026-04-13*
