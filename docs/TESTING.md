# 🧪 Testing Guide

This guide explains how to safely test **CaptainHook v3** on different environments.

---

## 🛠️ Environment 1: Local Linux (Host — Daily Driver)

Use this to quickly test changes without "infecting" your system (Melt/Persistence are disabled).

### Step 1: System Prerequisites
Install audio development headers:
```bash
sudo apt update && sudo apt install portaudio19-dev python3-all-dev
```

### Step 2: Virtual Environment
```bash
cd ~/Dokumente/Github/CaptainHook
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

### Step 3: Configuration
Edit `src/client/core/config.py` and replace the placeholders with your Discord Token and Guild ID:
```python
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
GUILD_ID = "1234567890123456789"
```

Or set the environment variable instead:
```bash
export DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN"
```

### Step 4: Run in Dev Mode
```bash
python -m src.client.main
```

### Step 5: Verify
- Check your Discord — the bot should appear online.
- Try: `$info`, `$shell ls`, `$ss`

---

## 🐧 Environment 2: Linux VM (VirtualBox)

Use this to test the compiled Linux binary in an isolated environment.

### Step 1: Build the Linux Client (on Host)

First, run the builder to stage with your credentials:
```bash
cd ~/Dokumente/Github/CaptainHook
python3 src/builder/main.py
# Select the 🧪 The Tester preset (Anti-VM and Melt disabled)
# Choose any disguise
```

Then compile natively (on Linux):
```bash
pyinstaller --onefile --noconsole --name CaptainHook build_staging/src/client/main.py
```

Or use Docker to build on Windows/Mac:
```bash
docker-compose up linux-builder
```

### Step 2: Transfer to VM
Copy `dist/CaptainHook` to your Linux Mint VM via shared folder or USB.

### Step 3: Run & Test
```bash
chmod +x CaptainHook
./CaptainHook
```

- Check Discord — bot should connect.
- Test `$shell ls`, `$info`, `$ss`
- If everything works, rebuild with the **👻 Ghost** preset to test Melt/Persistence in the VM.

---

## 🪟 Environment 3: Windows VM (VirtualBox / 2nd PC)

Use this to test the compiled Windows executable and the full Wraith Engine.

### Step 1: Build the Windows Client (on Linux Host)
```bash
cd ~/Dokumente/Github/CaptainHook
python3 src/builder/main.py
# Select the 🧪 The Tester preset first (safe for VMs)
# Choose Google Chrome disguise
docker-compose up windows-builder
```

The build may take 5-15 minutes. Output: `dist/CaptainHook.exe`

### Step 2: Transfer to Windows VM
Copy `dist/CaptainHook.exe` via shared folder, USB, or network share.

### Step 3: Run & Observe

**🧪 Tester Preset (Safe):**
- Double-click `CaptainHook.exe`
- Check Discord — bot should connect
- Test commands: `$info`, `$shell dir`, `$ss`
- The `.exe` should NOT delete itself or install persistence (safe for testing)

**👻 Ghost Preset (Real Test):**
- Rebuild with Ghost preset
- Transfer and run as **Administrator** (required for persistence)
- **Watch Task Manager** — the original `.exe` should disappear
- A new process should appear at `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\SystemData\winlogon_service.exe`
- **Reboot** the VM — the bot should reconnect automatically (persistence test)

### Step 4: Test Anti-VM (Full-Throttle Preset)
- Rebuild with **🛡️ Full-Throttle** on your VM
- If the VM has < 2 CPU cores or < 4GB RAM, the bot will exit immediately (Anti-VM working correctly)

---

## 🍎 Environment 4: macOS (Optional)

Most features (Shell, Screenshot, Keylogger) work via `pynput` and `mss`.

1. Follow the Linux instructions above.
2. Run `python -m src.client.main` directly (no Docker needed on macOS).
3. **Note:** macOS requires "Accessibility" permissions in System Preferences → Security & Privacy → Privacy → Accessibility for the Keylogger to work.

---

## ⚠️ Important Safety Notes

- **Always start with the 🧪 Tester preset** when testing on a new environment.
- **Never run Full-Throttle or Ghost on your daily driver** — it will install persistence and hide itself.
- **The Wraith Melt is irreversible** on the original executable — always keep a backup of your staged `build_staging/` folder.
- **Run Windows tests as Administrator** to verify elevated persistence features work correctly.
