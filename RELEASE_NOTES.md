# ⚓ CaptainHook v0.1.0 - Official Release

We are proud to announce the first major release of **CaptainHook (v0.1.0)**. This release marks the completion of Phase 4 and introduces a professional, highly-modular architecture for remote synchronization and management.

---

## 🚀 Key Features

### 🏗️ Architect Builder v3.1
*   **Instant Stub-Patching:** Generate bots in <1 second. No Python or compilers required for the end-user.
*   **Standalone Binaries:** Builder now available as a single executable for **Windows, Linux, and macOS**.
*   **Preset Support:** One-click generation for *Ghost (Stealth)*, *Full-Throttle*, and *The Tester* modes.
*   **Dockerized Compilation:** Fully fixed Wine environment for building Windows EXEs on Linux hosts.

### 🖥️ Developer TUI v2.5
*   **Live Event Monitoring:** Real-time system logs with aggressive auto-scrolling.
*   **Scrollable History:** Use `PgUp/PgDn` to review previous events (F10 focus-protected).
*   **System Stats (F2):** Real-time CPU, RAM, and Disk usage overlay.
*   **Stealth Toggle:** `F10` key to completely disable local input for maximum stealth.

### 🛡️ Core & Security
*   **Session Isolation:** Bots automatically create and lock into dedicated Discord channels (`hook-hostname-user`).
*   **Early Message Filtering:** Irrelevant commands are rejected at the event loop level to save host resources.
*   **Robust Lifecycle:** Reliable `$restart`, `$endsession`, and `$purge` (self-deletion) commands.
*   **Data Encryption:** New `$encrypt` and `$decrypt` commands using AES-256 (Fernet).

### 📺 Monitoring & Control
*   **Siren Engine:** Optimized Discord-native audio and camvid (H.264) streaming.
*   **Stealth Screenshotting:** Cross-platform support using `mss`.
*   **Professional Help System:** Category-based `$help` with alias support.

---

## 🛠️ Installation & Usage
1.  Download the `CaptainHookBuilder` for your OS from the Releases page.
2.  Run the builder and follow the interactive prompts (No dependencies needed!).
3.  Deploy the generated `CaptainHook.exe` (or binary) to the target machine.

---

## 📅 Roadmap to v0.2.0 (Phase 5)
*   [ ] **True Installer Mode:** Wrap bot in a disguised "Setup.exe".
*   [ ] **Persistent Status:** Pinned real-time status message in session channels.
*   [ ] **Advanced Browser Extraction:** Targeting Brave/Vivaldi on Linux.
*   [ ] **Anti-Analysis V2:** Behavioral sandbox detection.

---
*Stay Stealthy. Stay Synchronized.*
