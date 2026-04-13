# 🕹️ Command Usage Guide

CaptainHook uses a dedicated session channel for every remote machine. Look for a channel named `hook-[hostname]-[user]` in your Discord server.

The default command prefix is `$`.

---

## 📸 Spy & Media (Siren Engine)
- **`$ss`**: Captures a screenshot of the primary monitor.
- **`$screens`**: Lists all available monitors and their resolutions.
- **`$camshot`**: Takes a high-quality photo using the remote webcam.
- **`$camvid [seconds]`**: Records an AVI video with audio-sync.
- **`$audiorecord [seconds]`**: Captures high-fidelity `.wav` audio.
- **`$join <channel_name>`**: Joins a Discord voice channel for live streaming.
- **`$leave`**: Disconnects from the voice channel.
- **`$stream_audio`**: **Live Audio:** Streams system/mic audio directly to the voice channel.
- **`$stop_audio`**: Stops the live audio stream.
- **`$stream_visuals <mode> [interval]`**: Starts a live frame-stream (mode: `screen` or `cam`).
- **`$stop_stream`**: Halts the visual stream.
- **`$ears_start [secs]`**: **Offline Ears:** Bot caches audio clips every X seconds when disconnected (auto-uploads on reconnect).
- **`$ears_stop`**: Disables Offline Ears.

## ⌨️ Control & Input
- **`$press <key>`**: Presses a single key (e.g., `enter`, `win`, `space`).
- **`$type <text>`**: Types a string of text on the machine.
- **`$hotkey <key1> <key2>...`**: Performs complex key combinations (e.g., `ctrl` `alt` `del`).
- **`$click <x> <y>`**: Moves and clicks the mouse at specific coordinates.
- **`$block`**: Freezes all mouse and keyboard input (Windows Admin only).
- **`$unblock`**: Restores user input.
- **`$shutdown [reason]`**: Initiates a 10-second shutdown sequence.
- **`$reboot`**: Restarts the remote machine.

## 📂 File & Shell
- **`$ls [path]`**: Lists files and directories with clear indicators.
- **`$upload <path>`**: Sends a file from the target machine to Discord.
- **`$download <url> <filename>`**: Downloads a file from the internet to the target.
- **`$rm <path>`**: Deletes files or entire folders recursively.
- **`$mv <src> <dst>`**: Moves or renames files/folders.
- **`$shell <command>`**: Executes any shell command (PowerShell, CMD, or Bash).
- **`$pwd`**: Shows the current working directory.

## 🕵️ Information & Recon
- **`$info`**: Displays a rich Discord Embed with OS, hardware, and network details.
- **`$procs`**: Lists all active system processes.
- **`$passwords`**: Decrypts and extracts stored browser credentials (Chrome, Edge, Brave).
- **`$keylog_start`**: Begins background keylogging with window-title tracking.
- **`$keylog_stop`**: Stops the keylogger.
- **`$keylog_dump`**: Exports all captured keystrokes as a text file.

## 🎭 Fun & Trolling
- **`$msg <text>`**: Shows a system message box or notification.
- **`$wallpaper <url>`**: Changes the desktop wallpaper from a URL.
- **`$rickroll`**: Opens the RickRoll music video.
- **`$speak <text>`**: High-fidelity Text-to-Speech (TTS).
- **`$bsod`**: Triggers a real Windows Blue Screen of Death.

## ☢️ Destructive
- **`$nuke <path>`**: Recursively wipes a directory (USE WITH CAUTION).
- **`$nuke_desktop`**: Quick command to wipe the target's desktop files.

---

## 🖥️ Developer Mode (Interactive TUI)

When built with the **🛠️ Developer** preset, the bot launches a full-screen interactive dashboard on the remote machine.

### **Features:**
- **Live Output Log:** Every action the bot takes (Cog loading, connectivity, Discord messages) is displayed in real-time.
- **System Health:** Monitoring of the bot's CPU and RAM footprint.
- **Module Status:** Instant visual confirmation of which modules are active.
- **Safe Exit:** Use `CTRL+C` to shut down the bot gracefully.

### **Diagnostic Commands:**
- **`$p`**: **Ping Test:** Independent of modules. Verifies the bot is alive, reports hostname, and counts loaded Cogs. Use this if other commands fail.
- **`$reload <cog>`**: (Dev Only) Hot-reloads a module's code without restarting the bot.
