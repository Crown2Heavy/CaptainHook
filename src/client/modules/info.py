import os
import platform
import socket
import psutil
import uuid
import discord
from discord.ext import commands
from src.client.core.platform import Platform
from datetime import datetime
from ping3 import ping

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_size(self, bytes, suffix="B"):
        """Scale bytes to its proper format (e.g., GB, MB)."""
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor

    @commands.command(name="info", aliases=["sys"], help="Get a full detailed system information report.")
    async def system_info(self, ctx):
        try:
            embed = discord.Embed(title="🖥️ System Information", color=discord.Color.blue())
            
            # OS Info
            embed.add_field(name="OS", value=f"{platform.system()} {platform.release()} (v{platform.version()})", inline=False)
            embed.add_field(name="Hostname", value=socket.gethostname(), inline=True)
            embed.add_field(name="User", value=os.getlogin(), inline=True)
            
            # Hardware Info
            embed.add_field(name="CPU", value=f"{platform.processor()} ({psutil.cpu_count(logical=False)} Cores)", inline=False)
            
            # RAM
            svmem = psutil.virtual_memory()
            embed.add_field(name="RAM", value=f"{self.get_size(svmem.used)} / {self.get_size(svmem.total)}", inline=True)
            
            # Disk
            disk = psutil.disk_usage('/')
            embed.add_field(name="Disk", value=f"{self.get_size(disk.used)} / {self.get_size(disk.total)}", inline=True)
            
            # Network
            ip_addr = socket.gethostbyname(socket.gethostname())
            embed.add_field(name="Local IP", value=ip_addr, inline=True)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Info Error: {str(e)}")

    @commands.command(name="procs", help="List all running processes.")
    async def list_processes(self, ctx):
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                procs.append(f"{proc.info['pid']}: {proc.info['name']} ({proc.info['username']})")
            except:
                pass
        
        output = "\n".join(procs)
        if len(output) > 1900:
            file_path = "processes.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
            await ctx.send("📋 Process list:", file=discord.File(file_path))
            os.remove(file_path)
        else:
            await ctx.send(f"```\n{output}\n```")

    @commands.command(name="ping", aliases=["p"], help="Ping a specific IP or 8.8.8.8 to check connection.")
    async def ping_cmd(self, ctx, target: str = "8.8.8.8"):
        try:
            # Try ping3 first (cleaner)
            try:
                result = ping(target, unit='ms')
                if result:
                    await ctx.send(f"⚓ **Ping to {target}:** `{result:.2f} ms` (ping3)")
                    return
                else:
                    await ctx.send(f"❌ **Ping to {target} failed.** (ping3 timeout)")
                    return
            except PermissionError:
                # Common on Linux without sudo - fall back to system ping
                pass
            except Exception:
                pass

            # Fallback: System ping command
            import subprocess
            cmd = ["ping", "-c", "1", target] if not Platform.is_windows() else ["ping", "-n", "1", target]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            
            if proc.returncode == 0:
                output = stdout.decode()
                # Simple extraction of time for Linux/Windows
                if "time=" in output:
                    ping_time = output.split("time=")[1].split(" ")[0]
                    await ctx.send(f"⚓ **Ping to {target}:** `{ping_time}` (system fallback)")
                else:
                    await ctx.send(f"⚓ **Ping to {target}:** `Success` (system fallback)")
            else:
                await ctx.send(f"❌ **Ping to {target} failed.**\n`{stderr.decode()}`")

        except Exception as e:
            await ctx.send(f"❌ **Ping Error:** {str(e)}")

async def setup(bot):
    await bot.add_cog(Info(bot))
