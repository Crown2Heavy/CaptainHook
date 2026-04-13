import os
import sys
import time
import socket
import psutil
import logging
from datetime import datetime
from threading import Thread
from queue import Queue

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.logging import RichHandler

from src.client.core.config import Config
from src.client.core.platform import Platform

class TUILogHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        msg = self.format(record)
        self.queue.put(msg)

class DeveloperTUI:
    def __init__(self, bot):
        self.bot = bot
        self.console = Console()
        self.log_queue = Queue()
        self.logs = []
        self.max_logs = 20
        self.start_time = time.time()
        self.is_running = True

        # Setup Logging redirection
        self.setup_logging()

    def setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        handler = TUILogHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    def get_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="sidebar", size=30),
            Layout(name="body")
        )
        return layout

    def make_header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        status = "[bold green]ONLINE[/bold green]" if self.bot.is_ready() else "[bold red]CONNECTING[/bold red]"
        grid.add_row(
            f" ⚓ [bold cyan]CaptainHook Developer Console[/bold cyan] v{Config.VERSION}",
            f"Host: [yellow]{socket.gethostname()}[/yellow]",
            f"Status: {status} "
        )
        return Panel(grid, style="white on blue")

    def make_footer(self):
        elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start_time))
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        msg = f" [bold]UPTIME:[/bold] {elapsed} | [bold]CPU:[/bold] {cpu}% | [bold]RAM:[/bold] {ram}% | [bold red]CTRL+C to EXIT SAFELY[/bold red]"
        return Panel(msg, border_style="cyan")

    def make_sidebar(self):
        table = Table(title="[bold]Active Modules[/bold]", border_style="cyan", expand=True)
        table.add_column("Module", style="white")
        table.add_column("State", justify="right")
        
        # In Developer Mode, we show which modules loaded
        loaded_modules = [cog.lower() for cog in self.bot.cogs]
        all_possible = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]
        
        for mod in all_possible:
            state = "[green]●[/green]" if mod.capitalize() in self.bot.cogs else "[red]○[/red]"
            table.add_row(mod, state)
            
        return Panel(table, border_style="cyan")

    def make_log_view(self):
        # Process new logs
        while not self.log_queue.empty():
            self.logs.append(self.log_queue.get())
            if len(self.logs) > self.max_logs:
                self.logs.pop(0)

        log_text = Text()
        for log in self.logs:
            if "ERROR" in log:
                log_text.append(log + "\n", style="bold red")
            elif "INFO" in log:
                log_text.append(log + "\n", style="white")
            else:
                log_text.append(log + "\n", style="dim")
                
        return Panel(log_text, title="[bold]Live Output Log[/bold]", border_style="green")

    def run(self):
        layout = self.get_layout()
        
        with Live(layout, refresh_per_second=4, screen=True) as live:
            while self.is_running:
                layout["header"].update(self.make_header())
                layout["sidebar"].update(self.make_sidebar())
                layout["body"].update(self.make_log_view())
                layout["footer"].update(self.make_footer())
                time.sleep(0.2)

    def start(self):
        t = Thread(target=self.run, daemon=True)
        t.start()
