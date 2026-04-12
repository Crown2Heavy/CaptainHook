# 🧪 Testing Guide

This guide explains how to safely test **CaptainHook v3** on different environments.

---

## 🛠️ Environment 1: Local Linux (Linux Mint)
Since this is your daily driver, we want to test the bot without "infecting" your system (skipping the Melt/Persistence).

### **1. Linux System Prerequisites**
Before installing the Python dependencies, you must install the audio development headers on your system:
```bash
sudo apt update && sudo apt install portaudio19-dev python3-all-dev
```

### **2. Preparation**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install .
    ```
2.  **Configuration:**
    - Open `src/client/core/config.py`.
    - Manually enter your `DISCORD_TOKEN` and `GUILD_ID` for testing.
3.  **Run in "Dev Mode":**
    - To prevent the bot from moving itself and installing persistence, we will use the **Tester Preset** logic.
    - Run the bot directly:
      ```bash
      python -m src.client.main
      ```
4.  **Verification:**
    - Check your Discord. A new session channel should appear.
    - Try `$ss`, `$info`, and `$shell ls`.

---

## 🖥️ Environment 2: Windows VM (10/11)
This is where you test the **Architect Builder** and the **Wraith Engine**.

1.  **Build the Client (on your Host):**
    ```bash
    captainhook
    ```
    - Choose the **🧪 The Tester** preset first to ensure all features work.
    - Choose the **👻 Ghost** preset later to test the "Melt" and "Persistence" logic.
2.  **Transfer to VM:**
    - Move the generated `.exe` from the `dist/` folder to your VM (via shared folder or USB).
3.  **Run & Observe:**
    - Run the `.exe` as Administrator (to test `$block` and `$bsod`).
    - **Wraith Test:** Check if the original `.exe` deletes itself and if a new process appears in Task Manager under the disguised name.
    - **Persistence Test:** Reboot the VM and see if the bot reconnects automatically.

---

## 🍎 Environment 3: macOS VM (Optional)
Most features (Shell, Screenshot, Keylogger) will work via `pynput` and `mss`. 
- Follow the Linux instructions for the macOS terminal.
- Note: macOS requires "Accessibility" permissions for the Keylogger to work.
