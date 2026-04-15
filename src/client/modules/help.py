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
            category = category.lower().capitalize()
            if category in categories:
                await self.send_category_help(ctx, category, categories[category])
                return

        # Main Help Embed
        embed = discord.Embed(
            title="⚓ CaptainHook Command Menu",
            description=f"Remote Control & Monitoring System v{Config.VERSION}\nTarget: `{socket.gethostname()}`",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🚀 Quick Start",
            value=f"`{prefix}p` - Connectivity Test\n`{prefix}sh <cmd>` - Remote Shell\n`{prefix}ss` - Take Screenshot\n`{prefix}ls` - List Files",
            inline=False
        )

        # List categories
        cat_desc = ""
        for cat, cogs in categories.items():
            cat_desc += f"**{cat}** - `{prefix}help {cat.lower()}`\n"
        
        embed.add_field(name="📁 Categories", value=cat_desc, inline=False)
        
        # Common Aliases Section
        aliases_list = (
            f"`$ss` -> screenshot\n"
            f"`$sh` -> shell\n"
            f"`$ls` -> file_manager\n"
            f"`$p`  -> ping_test\n"
            f"`$h`  -> help"
        )
        embed.add_field(name="⌨️ Common Aliases", value=aliases_list, inline=True)

        footer_text = f"Use {prefix}help <category> for more details. | CaptainHook v{Config.VERSION}"
        embed.set_footer(text=footer_text)

        await ctx.send(embed=embed)

    async def send_category_help(self, ctx, category_name, cog_names):
        prefix = Config.COMMAND_PREFIX
        embed = discord.Embed(
            title=f"📁 Category: {category_name}",
            description=f"Commands available in the {category_name} module.",
            color=discord.Color.green()
        )

        for cog_name in cog_names:
            # Match cog name to actual Cog class name (usually Capitalized)
            actual_cog_name = cog_name.replace("_", " ").title().replace(" ", "")
            cog = self.bot.get_cog(actual_cog_name)
            
            if cog:
                commands_list = cog.get_commands()
                if commands_list:
                    cmd_info = ""
                    for cmd in commands_list:
                        if not cmd.hidden:
                            # Show aliases if they exist
                            alias_str = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                            cmd_info += f"**{prefix}{cmd.name}**{alias_str}: {cmd.help or 'No description'}\n"
                    
                    if cmd_info:
                        embed.add_field(name=f"📦 {actual_cog_name}", value=cmd_info, inline=False)

        if not embed.fields:
             embed.description = "No commands found for this category or modules not loaded."

        embed.set_footer(text=f"Use {prefix}help for the main menu.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
