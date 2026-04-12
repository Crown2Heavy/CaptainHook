# Captain Hook - Gemini Instructions

## Project Overview
Captain Hook is a cross-platform remote synchronization and management tool (for ethical use). It uses Discord as a Command & Control (C2) channel.

## Directory Structure
- `src/client/`: The code running on the remote machine.
  - `core/`: Core logic, platform abstraction, configuration, security.
  - `modules/`: Feature-specific logic (Keylogging, Screenshot, etc.).
  - `utils/`: Common helpers.
- `src/builder/`: The CLI builder to generate the client executable.
- `src/common/`: Shared code.
- `tests/`: Automated tests.
- `docs/`: Project documentation.

## Workflows

### Building the Client
1. Install dependencies: `pip install -r requirements.txt`
2. Run the builder: `python src/builder/main.py`
3. Provide the Discord Bot Token and Guild ID.
4. The builder will generate an executable in the `dist/` directory.

### Adding New Features
1. Create a new file in `src/client/modules/`.
2. Implement the feature as a Discord Cog.
3. Register the cog in `src/client/main.py`'s `setup_hook`.

## Engineering Standards
- **Cross-Platform:** Use the `Platform` class for any OS-specific paths or logic.
- **Modularity:** Keep the `core` minimal and use `modules` for functionality.
- **Security:** Do not commit hardcoded tokens. Use the builder's injection mechanism.
- **Styling:** Use `rich` for CLI interfaces.

## Core Requirements & Preferences
- **Persistence:** Implementation of platform-specific persistence (Windows Registry/Startup, Linux systemd/cron/desktop).
- **Stealth:** Integration of "Anti-Analysis" features (detecting VMs, Debuggers, Sandboxes).
- **Elevation:** Automatic elevation attempts (UAC bypass on Windows, sudo request/check on Linux).
- **Builder:** A professional, aesthetically pleasing CLI builder (similar to the Gemini CLI).

## Future Builder Enhancements
- **Build Presets:** Allow users to choose between "Tester" (VM-friendly), "Stealthy" (Maximum evasion), and "Fun/Trolling" (Visible/Interactive) versions.
- **Feature Selection:** "Tick-box" style CLI interface to include/exclude specific modules (e.g., disable keylogger to reduce size/detection).
- **Disguise & Spoofing:** Features to disguise the output executable as common system programs (e.g., changing icon, metadata, and filename).
- **One-File Output:** Ensure the builder always produces a single, standalone executable (`.exe` for Windows, binary for Linux) that bundles all dependencies for easy portability and stealth.

## The Infection Lifecycle (Dropper/Melt)
1.  **Lure:** Target runs the disguised executable (e.g., `Chrome_Setup.exe`).
2.  **Migration:** The file copies itself to a hidden, "legitimate" system path (e.g., `%APPDATA%\Microsoft\Windows\SearchData\mssearch.exe`).
3.  **Persistence:** Installs via Registry, Task Scheduler, or Systemd using the new path.
4.  **The Melt:** The original file (on USB or Downloads) is deleted automatically using a self-deletion script.
5.  **Ghost Execution:** The bot starts from the new hidden path, leaving no trace of the installer.

## Builder Presets
- **🛡️ Full-Throttle (All-in-One):** Every feature included. Maximum power, maximum size.
- **👻 Ghost (Extreme Stealth):** Focus on Shell, Screenshot, and Persistence. Stripped of "fun/trolling" features to minimize detection.
- **🧪 The Tester (VM Friendly):** All features active, but **Anti-VM and Persistence are DISABLED**. Used for safe local testing.
- **🤡 Troll-Mode (High Visibility):** Focus on Fun, Media, and Control commands. Designed to be interactive and visible.
- **⚙️ Custom:** Full manual control over every module and stealth setting.

## Roadmap / Next Steps
1.  **Siren Engine (Streaming/Offline):** Implement Discord-native audio streaming and the "Offline Caching" system.
2.  **Wraith Engine (Stealth/Persistence):** Implement "The Melt" (Dropper logic), file migration, and multi-layered persistence.
3.  **Architect Builder:** Create the final CLI builder with Preset support, Disguise/Icon spoofing, and the Infection configuration.
1.  **Stealth Screenshotting:** Implement cross-platform screenshotting using `mss` for Windows, Linux, and macOS support.
2.  **Advanced Keylogger:** Develop a professional keylogger using `pynput` for cross-platform event capturing.
3.  **Remote Shell:** Implement a dynamic shell handler that automatically detects and uses `cmd.exe`, `powershell`, or `/bin/bash` based on the host OS.
4.  **Browser Data Extraction:** Create modular extractors for Chrome and Firefox that work across Windows and Linux path structures.
5.  **Stealth & Persistence:** Enhance `src/client/core/security.py` with more advanced VM/Sandbox detection and multi-layered persistence methods.
