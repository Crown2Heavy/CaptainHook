# 🕹️ Command Usage Guide

This document provides a comprehensive list of all commands available in the CaptainHook client. Commands are grouped by module.

The default command prefix is `$`.

---

## 📸 Spy & Media
- **`$ss`**: Captures a screenshot of the primary monitor.
- **`$screens`**: Lists all available monitors and their resolutions.
- **`$camshot`**: Takes a high-quality photo using the remote webcam.
- **`$camvid [seconds]`**: Records an AVI video with audio-sync.
- **`$audiorecord [seconds]`**: Captures high-fidelity `.wav` audio.
- **`$join <channel_name>`**: Joins a Discord voice channel to start live audio/visual streaming.
- **`$stream_visuals <mode> [interval]`**: Starts a live frame-stream (mode: `screen` or `cam`).
- **`$stop_stream`**: Halts the visual stream.
- **`$leave`**: Disconnects from the voice channel.

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
