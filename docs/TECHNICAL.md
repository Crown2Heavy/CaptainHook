# 🏗️ Technical Architecture

This document provides a deep dive into the underlying engines and logic that power CaptainHook.

---

## 1. The Siren Engine (Streaming & Connectivity)

### **Network Resilience**
The bot maintains a background heartbeat task that monitors internet connectivity. If the connection to Discord is lost, the bot enters "Offline Mode."

### **Encrypted Offline Caching**
While offline, certain modules (like the Keylogger) can save data to a hidden, encrypted cache.
- **Encryption:** AES-128 via the `Fernet` library.
- **Location:** `%APPDATA%\.CaptainHook\.cache` (Windows) or `~/.local/share/.CaptainHook/.cache` (Linux).
- **Auto-Recovery:** Upon reconnection, the bot automatically decrypts, uploads, and wipes all cached data.

### **Discord-Native Streaming**
Live audio is streamed using the Discord Voice protocol (`discord[voice]` + `PyNaCl`). Visuals are streamed as a series of high-frequency frames with a controlled `delete_after` TTL to simulate a real-time feed without cluttering the channel.

---

## 2. The Wraith Engine (Stealth & Persistence)

### **The "Melt" (Dropper Lifecycle)**
When the initial executable is run, the Wraith Engine performs a one-time migration:
1.  Copies the current binary to a hidden system path (e.g., `...\Microsoft\Windows\SystemData\winlogon_service.exe`).
2.  Sets the file attributes to **Hidden** and **System**.
3.  Installs advanced persistence for the *new* path.
4.  Launches the new process and triggers a self-deletion script for the original file.

### **Advanced Persistence**
- **Windows:** Uses the Task Scheduler (`schtasks`) to create a task that runs at every user login with highest privileges.
- **Linux:** Creates a `systemd` user service with an `always-restart` policy.

---

## 3. Modular System (Extensibility)

The bot is built on the `discord.ext.commands` framework. Each feature group is a separate **Cog** in `src/client/modules/`.

```python
# Example of a modular command
class MyFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mycmd")
    async def my_command(self, ctx):
        await ctx.send("Feature working!")
```

To add a feature, create a new module and register it in `src/client/main.py`.

---

## 4. Encryption & Security

- **Credential Injection:** The Architect Builder performs "Static Injection" during the build process, replacing placeholders in the source code with your actual credentials.
- **Data Protection:** Browser passwords are decrypted on the fly using **Windows DPAPI** and **AES-GCM**, ensuring that no raw decryption keys are ever stored on disk.
