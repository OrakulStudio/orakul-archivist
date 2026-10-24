import hashlib
import json
import os
from pathlib import Path
import sys
import time

if os.name == 'nt':
    import msvcrt

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SCRIPT_DIR / "archivist_folders.json"
STATE_FILE = SCRIPT_DIR / "archivist_baseline.json"
REPORT_FILE = SCRIPT_DIR / "archivist_last_changes.txt"

CURRENT_LANG = "ru"
TRANSLATIONS = {}

def init_i18n(config):
    global CURRENT_LANG, TRANSLATIONS
    CURRENT_LANG = config.get("language", "ru")
    lang_file = SCRIPT_DIR / f"{CURRENT_LANG}.json"
    if lang_file.exists():
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                TRANSLATIONS = json.load(f)
        except Exception:
            TRANSLATIONS = {}

def t(text: str) -> str:
    if CURRENT_LANG == "en":
        return text
    return TRANSLATIONS.get(text, text)

def clean_path(raw_path):
    if not raw_path:
        return ""
    return raw_path.strip().strip('"').strip("'").strip()

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                cfg["exclude_dirs"] = []
                if "language" not in cfg:
                    cfg["language"] = "ru"
                return cfg
        except Exception:
            pass
    return {"watched_folders": [], "exclude_dirs": [], "language": "ru"}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        return True
    except Exception:
        return False

def load_baseline():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_baseline(state):
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass

# УЛЬТРА-БЫСТРЫЙ СКАНЕР ДИСКА (ФАЙЛЫ + ПАПКИ)
def scan_folders(folders):
    state = {}
    for folder_str in folders:
        folder_path = os.path.abspath(clean_path(folder_str))
        if not os.path.exists(folder_path):
            continue
        
        stack = [folder_path]
        while stack:
            curr_dir = stack.pop()
            try:
                with os.scandir(curr_dir) as entries:
                    for entry in entries:
                        try:
                            norm_key = os.path.abspath(entry.path)
                            st = entry.stat(follow_symlinks=False)
                            
                            if entry.is_dir(follow_symlinks=False):
                                stack.append(entry.path)
                                state[norm_key + "\\"] = {
                                    "hash": f"DIR:{st.st_mtime}",
                                    "mtime": st.st_mtime
                                }
                            elif entry.is_file(follow_symlinks=False):
                                state[norm_key] = {
                                    "hash": f"STAT:{st.st_size}_{st.st_mtime}",
                                    "mtime": st.st_mtime
                                }
                        except OSError:
                            continue
            except OSError:
                continue
    return state

def format_mtime(mtime_val):
    try:
        if isinstance(mtime_val, (int, float)):
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime_val))
        return str(mtime_val)
    except Exception:
        return "N/A"

def compare_states(baseline_state, current_state):
    added = []
    modified = []
    deleted = []

    for path, data in baseline_state.items():
        if path not in current_state:
            deleted.append(path)
        elif current_state[path]["hash"] != data["hash"]:
            modified.append((path, current_state[path]["mtime"]))

    for path, data in current_state.items():
        if path not in baseline_state:
            added.append((path, data["mtime"]))

    return added, modified, deleted

# АВТОМАТИЧЕСКИЙ ЭКСПОРТ ОТЧЁТА В ТЕКСТОВЫЙ ФАЙЛ ПРИ ВЫХОДЕ
def export_report_if_needed(added, modified, deleted):
    if not added and not modified and not deleted:
        return False

    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(f"=== ORAKUL ARCHIVIST REPORT [{time.strftime('%Y-%m-%d %H:%M:%S')}] ===\n\n")
            if added:
                f.write(f"--- NEW ITEMS ({len(added)}) ---\n")
                for path, mtime in added:
                    f.write(f"[+] {path} (Modified: {format_mtime(mtime)})\n")
                f.write("\n")

            if modified:
                f.write(f"--- MODIFIED ITEMS ({len(modified)}) ---\n")
                for path, mtime in modified:
                    f.write(f"[~] {path} (Modified: {format_mtime(mtime)})\n")
                f.write("\n")

            if deleted:
                f.write(f"--- DELETED ITEMS ({len(deleted)}) ---\n")
                for path in deleted:
                    f.write(f"[-] {path}\n")
                f.write("\n")
        return True
    except Exception:
        return False

def make_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="sidebar", size=42),
        Layout(name="body", ratio=1)
    )
    return layout

def generate_header(status_msg: str) -> Panel:
    title_str = t("[bold cyan]ORAKUL ARCHIVIST[/bold cyan] [dim]| System Watchdog TUI v1.0[/dim]")
    status_str = f" [bold green]• {status_msg}[/bold green]" if status_msg else ""
    return Panel(f"{title_str}{status_str}", border_style="cyan")

def generate_footer() -> Panel:
    footer_text = t(
        "[dim]Actions:[/dim] [bold cyan][Enter/Space][/bold cyan] [dim]Scan |[/dim] "
        "[bold cyan][↑/↓][/bold cyan] [dim]Scroll |[/dim] "
        "[bold cyan][+][/bold cyan] [dim]Add |[/dim] "
        "[bold cyan][-][/bold cyan] [dim]Remove |[/dim] "
        "[bold yellow][R][/bold yellow] [dim]Reset |[/dim] "
        "[bold magenta][L][/bold magenta] [dim]Lang |[/dim] "
        "[bold red][Q][/bold red] [dim]Quit[/dim]"
    )
    return Panel(footer_text, border_style="dim")

def generate_sidebar(config, total_files, last_scan_time) -> Panel:
    folders = config.get("watched_folders", [])
    
    table = Table(box=None, expand=True, show_header=False)
    table.add_column("Index", style="bold cyan", width=3)
    table.add_column("Path", style="bright_white", overflow="ellipsis")

    if not folders:
        table.add_row("", t("[bold yellow]⚠️ No tracked folders configured yet.[/bold yellow]"))
    else:
        for idx, f in enumerate(folders, 1):
            table.add_row(f"{idx}.", f)

    content = Table.grid(expand=True)
    content.add_row(table)
    content.add_row("\n[dim]──────────────────────────────────────────[/dim]")
    content.add_row(f"[bold yellow]{t('Total Files Indexed')}:[/bold yellow] [bold green]{total_files}[/bold green]")
    content.add_row(f"[bold yellow]{t('Last Scan')}:[/bold yellow] [dim]{last_scan_time}[/dim]")

    return Panel(content, title=t("📁 Tracked Directories"), border_style="cyan")

def generate_body(baseline_state, current_state, scroll_offset=0) -> Panel:
    added, modified, deleted = compare_states(baseline_state, current_state)
    
    all_changes = []
    for path, mtime in added:
        all_changes.append(("NEW", path, format_mtime(mtime)))
    for path, mtime in modified:
        all_changes.append(("MOD", path, format_mtime(mtime)))
    for path in deleted:
        all_changes.append(("DEL", path, t("N/A")))

    total_changes = len(all_changes)

    if total_changes == 0:
        return Panel(
            f"\n\n[bold green]  {t('✨ PERFECT MATCH — NO LOCAL CHANGES DETECTED!')}[/bold green]\n"
            f"  [dim]{t('All tracked files match your saved baseline snapshot.')}[/dim]",
            title=t("🔍 Detected Code & File Changes"),
            border_style="yellow"
        )

    PAGE_SIZE = 14
    max_offset = max(0, total_changes - PAGE_SIZE)
    scroll_offset = min(scroll_offset, max_offset)

    visible_items = all_changes[scroll_offset : scroll_offset + PAGE_SIZE]

    table = Table(box=box.SIMPLE_HEAD, expand=True)
    table.add_column(t("Status"), style="bold", width=12)
    table.add_column(t("File Path"), style="bright_white", overflow="ellipsis")
    table.add_column(t("Last Modified"), style="dim", width=20)

    for st_type, path, mtime in visible_items:
        if st_type == "NEW":
            table.add_row(t("[bold green]+ NEW[/bold green]"), path, mtime)
        elif st_type == "MOD":
            table.add_row(t("[bold yellow]~ MODIFIED[/bold yellow]"), path, mtime)
        elif st_type == "DEL":
            table.add_row(t("[bold red]- DELETED[/bold red]"), path, mtime)

    grid = Table.grid(expand=True)
    grid.add_row(table)
    
    page_info = f"Показано {scroll_offset + 1}-{min(scroll_offset + PAGE_SIZE, total_changes)} из {total_changes} | Используйте [↑/↓] для прокрутки"
    grid.add_row(f"\n[dim]{page_info}[/dim]")

    title_str = f"🔍 {t('Detected Code & File Changes')} ({total_changes})"
    return Panel(grid, title=title_str, border_style="yellow")

def get_keypress():
    if os.name == 'nt':
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                if ch2 == b'H':  # Up Arrow
                    return 'up'
                elif ch2 == b'P':  # Down Arrow
                    return 'down'
            try:
                if ch in (b'\r', b'\n', b' '):
                    return 'scan'
                return ch.decode('utf-8').lower()
            except Exception:
                return None
    return None

def main():
    config = load_config()
    init_i18n(config)

    folders = config.get("watched_folders", [])

    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(f"\n  [bold cyan]... {t('Loading and indexing files... Please wait...')} ...[/bold cyan]\n")

    current_state = scan_folders(folders)
    baseline_state = load_baseline()

    if not baseline_state and current_state:
        baseline_state = current_state.copy()
        save_baseline(baseline_state)

    last_scan = time.strftime("%H:%M:%S")
    status_msg = t("Ready")
    scroll_offset = 0

    layout = make_layout()

    with Live(layout, refresh_per_second=4, screen=True) as live:
        while True:
            layout["header"].update(generate_header(status_msg))
            layout["footer"].update(generate_footer())
            layout["sidebar"].update(generate_sidebar(config, len(current_state), last_scan))
            layout["body"].update(generate_body(baseline_state, current_state, scroll_offset))

            key = get_keypress()

            if key == 'up':
                scroll_offset = max(0, scroll_offset - 1)

            elif key == 'down':
                scroll_offset += 1

            elif key == 'scan':
                status_msg = t("Scanning...")
                layout["header"].update(generate_header(status_msg))
                live.refresh()

                current_state = scan_folders(config.get("watched_folders", []))
                last_scan = time.strftime("%H:%M:%S")
                status_msg = f"{t('Scanned at')} {last_scan}"

            elif key == '+':
                live.stop()
                console.print(t("\n[bold cyan]Drag & Drop Folder (or Enter to finish): [/bold cyan]"), end="")
                user_input = input()
                cleaned = clean_path(user_input)
                if cleaned and Path(cleaned).exists():
                    f_list = config.get("watched_folders", [])
                    abs_cleaned = os.path.abspath(cleaned)
                    if abs_cleaned not in f_list:
                        f_list.append(abs_cleaned)
                        config["watched_folders"] = f_list
                        save_config(config)

                        new_folder_state = scan_folders([abs_cleaned])
                        baseline_state.update(new_folder_state)
                        save_baseline(baseline_state)

                        current_state = scan_folders(f_list)
                        last_scan = time.strftime("%H:%M:%S")
                        status_msg = t("Folder added!")
                live.start()

            elif key == '-':
                live.stop()
                f_list = config.get("watched_folders", [])
                if f_list:
                    console.print(t("\n[bold cyan]Enter folder # to remove (or 'all' to clear config): [/bold cyan]"), end="")
                    choice = input().strip().lower()
                    if choice == "all":
                        config["watched_folders"] = []
                        save_config(config)
                        if STATE_FILE.exists():
                            os.remove(STATE_FILE)
                        baseline_state = {}
                        current_state = {}
                        status_msg = t("All folders cleared!")
                    elif choice.isdigit():
                        num = int(choice)
                        if 1 <= num <= len(f_list):
                            removed_folder = f_list.pop(num - 1)
                            config["watched_folders"] = f_list
                            save_config(config)

                            removed_path_str = os.path.abspath(removed_folder)
                            baseline_state = {k: v for k, v in baseline_state.items() if not k.startswith(removed_path_str)}
                            save_baseline(baseline_state)

                            current_state = scan_folders(f_list)
                            status_msg = t("Folder removed!")
                last_scan = time.strftime("%H:%M:%S")
                live.start()

            elif key == 'r':
                current_state = scan_folders(config.get("watched_folders", []))
                baseline_state = current_state.copy()
                save_baseline(baseline_state)
                scroll_offset = 0
                last_scan = time.strftime("%H:%M:%S")
                status_msg = t("Baseline reset!")

            elif key == 'l':
                config["language"] = "ru" if config.get("language", "en") == "en" else "en"
                save_config(config)
                init_i18n(config)
                status_msg = t("Language changed")

            elif key == 'q':
                # ПРИ ВЫХОДЕ: сохраняем текстовый лог изменений и фиксируем эталон
                added, modified, deleted = compare_states(baseline_state, current_state)
                if export_report_if_needed(added, modified, deleted):
                    console.print(f"\n[bold green]✓ Report saved to {REPORT_FILE.name}[/bold green]")
                
                # Обновляем базу на текущий момент, чтобы следующий запуск был чистым
                save_baseline(current_state)
                break

            time.sleep(0.05)

    console.print("[bold cyan]Orakul Archivist TUI closed. Goodbye![/bold cyan]")

if __name__ == "__main__":
    main()