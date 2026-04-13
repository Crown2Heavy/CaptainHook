import os
import shutil
import aiohttp
import discord
from discord.ext import commands
from src.client.core.platform import Platform

class FileManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ls", help="List files in the current directory.")
    async def list_files(self, ctx, path="."):
        try:
            # Ensure we use an absolute path for listing if provided
            target_path = os.path.abspath(path)
            if not os.path.exists(target_path):
                 await ctx.send(f"❌ Path not found: `{path}`")
                 return

            files = os.listdir(target_path)
            if not files:
                await ctx.send(f"📁 Directory is empty: `{target_path}`")
                return
            
            output = f"📁 **Directory listing for `{target_path}`**\n"
            for f in files:
                is_dir = os.path.isdir(os.path.join(target_path, f))
                prefix = "📁" if is_dir else "📄"
                output += f"{prefix} {f}\n"
            
            if len(output) > 1900:
                file_path = "ls_output.txt"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output)
                await ctx.send("📄 Listing too long, sending as file:", file=discord.File(file_path))
                os.remove(file_path)
            else:
                await ctx.send(output)
        except Exception as e:
            await ctx.send(f"❌ Error listing files: {str(e)}")

    @commands.command(name="upload", help="Upload a file from the remote machine to Discord.")
    async def upload(self, ctx, file_path):
        if not os.path.exists(file_path):
            await ctx.send(f"❌ File not found: `{file_path}`")
            return
        
        if os.path.isdir(file_path):
             await ctx.send(f"❌ `{file_path}` is a directory. Please specify a file.")
             return

        try:
            file_size = os.path.getsize(file_path)
            if file_size > 25 * 1024 * 1024: # 25MB limit
                await ctx.send(f"⚠️ File is too large ({file_size / 1024 / 1024:.2f}MB). Discord limit is 25MB.")
                return

            await ctx.send(f"📤 Uploading `{os.path.basename(file_path)}`...")
            await ctx.send(file=discord.File(file_path))
        except Exception as e:
            await ctx.send(f"❌ Upload Error: {str(e)}")

    @commands.command(name="download", help="Download a file from a URL to the remote machine.")
    async def download(self, ctx, url, filename):
        try:
            await ctx.send(f"📥 Downloading `{filename}` from URL...")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(filename, 'wb') as f:
                            f.write(content)
                        await ctx.send(f"✅ Download complete: `{os.path.abspath(filename)}`")
                    else:
                        await ctx.send(f"❌ Download failed with status: {response.status}")
        except Exception as e:
            await ctx.send(f"❌ Download Error: {str(e)}")

    @commands.command(name="rm", help="Remove a file or directory.")
    async def remove(self, ctx, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
                await ctx.send(f"✅ Deleted file: `{path}`")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                await ctx.send(f"✅ Deleted directory: `{path}`")
            else:
                await ctx.send(f"❌ Path not found: `{path}`")
        except Exception as e:
            await ctx.send(f"❌ Delete Error: {str(e)}")

    @commands.command(name="mv", help="Move or rename a file/directory.")
    async def move(self, ctx, src, dst):
        try:
            shutil.move(src, dst)
            await ctx.send(f"✅ Moved `{src}` to `{dst}`")
        except Exception as e:
            await ctx.send(f"❌ Move Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(FileManager(bot))
