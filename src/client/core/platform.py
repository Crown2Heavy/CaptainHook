import os
import platform
import sys

class Platform:
    @staticmethod
    def is_windows():
        return platform.system() == "Windows"

    @staticmethod
    def is_linux():
        return platform.system() == "Linux"

    @staticmethod
    def is_macos():
        return platform.system() == "Darwin"

    @staticmethod
    def get_appdata_path(local=False):
        if local:
            # If local is requested (Developer Mode), use a folder in the current directory
            local_path = os.path.join(os.getcwd(), ".data")
            os.makedirs(local_path, exist_ok=True)
            return local_path

        if Platform.is_windows():
            return os.environ.get('APPDATA')
        elif Platform.is_linux() or Platform.is_macos():
            return os.path.expanduser("~/.local/share")
        return os.path.expanduser("~")

    @staticmethod
    def get_temp_path():
        if Platform.is_windows():
            return os.environ.get('TEMP')
        return "/tmp"

    @staticmethod
    def get_home_path():
        return os.path.expanduser("~")

    @staticmethod
    def get_system_info():
        return {
            "os": platform.system(),
            "version": platform.version(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "node": platform.node()
        }
