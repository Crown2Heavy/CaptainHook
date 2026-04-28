import discord
from discord.ext import commands
import socket
from src.client.core.config import Config

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h", "commands"], help="Display the CaptainHook command menu.")
    async def help_command(self, ctx, category: str = None):
        """Custom help command with categories and embeds."""
        prefix = Config.COMMAND_PREFIX
        
        # Category mapping for cleaner display
        categories = {
            "Core": ["control", "info", "help"],
            "System": ["shell", "file_manager", "nuke", "encryption"],
            "Monitoring": ["screenshot", "keylogger", "media", "browser"],
            "Fun": ["fun"]
        }

        if category:
            category_key = category.lower().capitalize()
            if category_key in categories:
                await self.send_category_help(ctx, category_key, categories[category_key])
                return

        # Main Help Embed
        embed = discord.Embed(
            title="⚓ CaptainHook v" + Config.VERSION,
            description=(
                f"**Remote Management Interface**\n"
                f"Host: `{socket.gethostname()}`\n"
                f"Prefix: `{prefix}`\n\n"
                f"Use `{prefix}help <category>` to see all commands in a group."
            ),
            color=0x2b2d31 # Dark Discord theme color
        )

        # Quick Links/Highlights
        quick_start = (
            f"⚡ `{prefix}p` - Connectivity Check\n"
            f"🐚 `{prefix}sh` - Remote Shell\n"
            f"📸 `{prefix}ss` - Screenshot\n"
            f"📂 `{prefix}ls` - File Manager"
        )
        embed.add_field(name="🚀 Quick Access", value=quick_start, inline=False)

        # Categories
        cat_links = " | ".join([f"`{c}`" for c in categories.keys()])
        embed.add_field(name="📁 Command Categories", value=cat_links, inline=False)

        # Detail on how to use
        embed.add_field(
            name="⌨️ Example Usage",
            value=f"`{prefix}help System` - Show system management commands\n`{prefix}help Core` - Show bot control commands",
            inline=False
        )

        embed.set_thumbnail(url="https://raw.githubusercontent.com/Rich-Ian/CaptainHook/main/Captain%20Hook.ico")
        embed.set_footer(text=f"CaptainHook | Crafted for efficiency.")

        await ctx.send(embed=embed)

    async def send_category_help(self, ctx, category_name, cog_names):
        prefix = Config.COMMAND_PREFIX
        embed = discord.Embed(
            title=f"📁 Category: {category_name}",
            description=f"Detailed list of commands within the {category_name} module.",
            color=0x3498db # Nice blue
        )

        found_commands = False
        for cog_name in cog_names:
            # Match cog name to actual Cog class name (usually Capitalized)
            # Normalizing naming convention: module 'file_manager' -> Cog 'FileManager'
            actual_cog_name = "".join([word.capitalize() for word in cog_name.split("_")])
            cog = self.bot.get_cog(actual_cog_name)
            
            if cog:
                commands_list = cog.get_commands()
                if commands_list:
                    cmd_info = ""
                    for cmd in commands_list:
                        if not cmd.hidden:
                            alias_str = f"| `{', '.join(cmd.aliases)}`" if cmd.aliases else ""
                            cmd_info += f"**`{prefix}{cmd.name}`** {alias_str}\n└ {cmd.help or 'No description'}\n"
                    
                    if cmd_info:
                        embed.add_field(name=f"📦 {actual_cog_name}", value=cmd_info, inline=False)
                        found_commands = True

        if not found_commands:
             embed.description = "❌ No modules or commands found for this category."
             embed.color = discord.Color.red()

        embed.set_footer(text=f"Use {prefix}help for the main menu.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
