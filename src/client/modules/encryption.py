import os
import discord
from discord.ext import commands
from cryptography.fernet import Fernet
import io

class Encryption(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="genkey", help="Generate a new encryption key.")
    async def generate_key(self, ctx):
        key = Fernet.generate_key()
        await ctx.author.send(f"🔐 **New Encryption Key Generated**\nKeep this safe! You need it to decrypt files.\n`{key.decode()}`")
        await ctx.send("✅ Key generated and sent to your DMs for security.")

    @commands.command(name="encrypt", help="Encrypt a file on the host. Usage: $encrypt <path> <key>")
    async def encrypt_file(self, ctx, path: str, key: str):
        if not os.path.exists(path):
            await ctx.send(f"❌ File not found: `{path}`")
            return

        try:
            f = Fernet(key.encode())
            with open(path, "rb") as file:
                file_data = file.read()
            
            encrypted_data = f.encrypt(file_data)
            
            with open(path, "wb") as file:
                file.write(encrypted_data)
            
            await ctx.send(f"🔒 File encrypted successfully: `{path}`")
        except Exception as e:
            await ctx.send(f"❌ Encryption Error: {str(e)}")

    @commands.command(name="decrypt", help="Decrypt a file on the host. Usage: $decrypt <path> <key>")
    async def decrypt_file(self, ctx, path: str, key: str):
        if not os.path.exists(path):
            await ctx.send(f"❌ File not found: `{path}`")
            return

        try:
            f = Fernet(key.encode())
            with open(path, "rb") as file:
                file_data = file.read()
            
            decrypted_data = f.decrypt(file_data)
            
            with open(path, "wb") as file:
                file.write(decrypted_data)
            
            await ctx.send(f"🔓 File decrypted successfully: `{path}`")
        except Exception as e:
            await ctx.send(f"❌ Decryption Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Encryption(bot))
