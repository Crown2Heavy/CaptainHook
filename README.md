# 🔱 CaptainHook v3.0

> **A professional, modular, and cross-platform remote management and synchronization suite.**

CaptainHook is a high-performance Command & Control (C2) tool designed for ethical remote administration. It leverages the Discord API as a reliable communication channel, providing a seamless experience for managing remote machines across Windows, Linux, and macOS.

---

## ✨ Key Features

- **🌐 Cross-Platform:** Native support for Windows 10/11/12, Linux (Mint, Ubuntu, etc.), and macOS.
- **🛠️ Architect Builder:** Professional CLI tool with presets (Ghost, Full-Throttle, Tester) and disguise capabilities.
- **🛡️ Wraith Engine:** Advanced stealth, "The Melt" dropper logic, and multi-layered persistence.
- **📡 Siren Engine:** Discord-native audio/visual streaming and encrypted offline caching.
- **🔐 Modular Design:** Easily extend or remove features via the plug-and-play module system.

---

## 🚀 Quick Start

### 1. Requirements
Install the necessary dependencies on your development machine:
```bash
pip install -r requirements.txt
```

### 2. The Builder
Launch the **Architect Builder** to generate your client:
```bash
python src/builder/main.py
```
1.  **Enter Credentials:** Provide your Discord Bot Token and Guild ID.
2.  **Select Preset:** Choose a pre-configured mode (e.g., `👻 Ghost` for maximum stealth).
3.  **Select Disguise:** Choose a template (e.g., `Google Chrome`) to spoof the icon and metadata.
4.  **Deploy:** The builder will prepare a "Staged" version of the client ready for compilation.

---

## 📂 Documentation

For deep dives into the system, refer to the following guides:

- **[🛠️ Builder Configuration](./docs/BUILDER.md):** Detailed guide on presets, disguises, and the compilation process.
- **[🕹️ Command Usage](./docs/USAGE.md):** Complete list of commands and their functions.
- **[🏗️ Technical Architecture](./docs/TECHNICAL.md):** Overview of the Siren and Wraith engines, encryption, and the modular system.
- **[📜 Development Log](./docs/DEVELOPMENT_LOG.md):** Roadmap and project history.

---

## ⚠️ Disclaimer
This tool is for educational and ethical use only. Unauthorized access to remote systems is illegal. The author takes no responsibility for misuse of this software.

---

## 🛠️ Created by
**[ThatsCode]**
*A member of the Thats.it Team.*
