import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from rich.console import Console
from rich.panel import Panel

# Enforce UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console()

GITHUB_USER = 'OrakulStudio'
REPO_NAME = 'orakul-archivist'  
REPO_ZIP_URL = f'https://github.com/{GITHUB_USER}/{REPO_NAME}/archive/refs/heads/main.zip'


def get_local_commit_hash():
    """Get the current local commit hash (if git is initialized)."""
    try:
        hash_val = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'], stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        return hash_val
    except Exception:
        return None


def get_remote_commit_hash():
    """Get the latest commit hash from GitHub API."""
    url = f'https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/commits/main'
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Orakul-Archivist-Updater'}
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data['sha'][:7]
    except Exception:
        pass
    return None


def download_and_extract_full_repo(target_dir='.'):
    """Downloads the full repository as a ZIP and safely updates local files."""
    
    # EXCLUDED ITEMS: The script will NEVER delete or overwrite these configs/baselines/reports.
    exclude_items = {
        'archivist_folders.json',
        'archivist_baseline.json',
        'archivist_last_changes.txt',
        'venv',          
        '.venv_archivist',
        '.git',          
        '__pycache__'    
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'update.zip')

        with console.status(
            '[bold yellow]⏳ Downloading a fresh core archive from GitHub...[/bold yellow]',
            spinner='dots',
        ):
            try:
                urllib.request.urlretrieve(REPO_ZIP_URL, zip_path)
            except Exception as e:
                console.print(f'[bold red]❌ Download error: {e}[/bold red]')
                return False

        with console.status(
            '[bold yellow]📦 Unpacking and preparing files...[/bold yellow]',
            spinner='dots',
        ):
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            except Exception as e:
                console.print(f'[bold red]❌ Unpack error: {e}[/bold red]')
                return False

        extracted_folders = [
            f for f in os.listdir(temp_dir)
            if os.path.isdir(os.path.join(temp_dir, f)) and f != '__MACOSX'
        ]
        if not extracted_folders:
            console.print('[bold red]❌ Archive structure error.[/bold red]')
            return False

        source_dir = os.path.join(temp_dir, extracted_folders[0])

        with console.status(
            '[bold yellow]📂 Safely updating files...[/bold yellow]',
            spinner='dots',
        ):
            for item in os.listdir(source_dir):
                if item in exclude_items:
                    continue 

                s_path = os.path.join(source_dir, item)
                d_path = os.path.join(target_dir, item)

                try:
                    if os.path.isdir(s_path):
                        if os.path.exists(d_path):
                            shutil.rmtree(d_path)
                        shutil.copytree(s_path, d_path)
                    else:
                        shutil.copy2(s_path, d_path)
                except Exception as e:
                    console.print(f'[yellow]⚠️ Failed to update {item}: {e}[/yellow]')

    return True


def print_banner():
    console.print(r""" [bold cyan]                                
 █▀█ █▀█ ▄▀█ █▄▀ █░█ █░ █   ▄▀█ █▀█ █▀▀ █ █░█ █ █▀ ▀█▀   █░█ █ █▀   █▀█ █▀█ █▀█ ▄▀█ █▀▀ █ █▀ █ █▀▀
 █▀▄ █▀▄ █▀█ █░█ █▄█ █▄ █   █▀█ █▀▄ █▄▄ █ ▀▄▀ █ ▄█ ░█░   █▀█ █ ▄█   █▀▄ █▀▄ █▀█ █▀█ █▄▄ █ ▄█ █ █▄▄                                                                                                                                                                                                           
    """)


def draw_whats_new():
    changelog = (
        '[bold cyan]ℹ️ WHAT`S NEW (v1.0):[/bold cyan]\n\n'
        '  [bold]— Orakul Archivist TUI v1.0 —[/bold]\n'
        '  High-performance filesystem watchdog (140k+ files in <0.2s).\n\n'
        '  [bold]— Smart Change Tracking —[/bold]\n'
        '  Precise detection of new, modified, and deleted items.\n\n'
        '  [bold]— Auto-Reporting & Safety —[/bold]\n'
        '  Automatic changelog export (archivist_last_changes.txt) on [Q] exit.\n\n'
        '  [bold]— Zero Configuration Loss —[/bold]\n'
        '  Watched directories and baseline snapshots are safely preserved during updates.'
    )

    console.print(
        Panel(
            changelog,
            title='[bold yellow]📁 ORAKUL ARCHIVIST[/bold yellow]',
            title_align='left',
            subtitle='[bold cyan]Version: 1.0.0[/bold cyan]',
            subtitle_align='right',
            border_style='cyan',
            expand=False,
        )
    )


def check_for_updates():
    console.print("\n[dim]Checking for updates on GitHub...[/dim]")
    
    local_hash = get_local_commit_hash()
    remote_hash = get_remote_commit_hash()

    if not remote_hash:
        console.print("[bold red]❌ Failed to connect to GitHub. Check your internet connection.[/bold red]")
        return

    if local_hash != remote_hash or local_hash is None:
        console.print('\n' + '=' * 55)
        print_banner()
        draw_whats_new()
        console.print(
            f'\n🚀 [bold yellow]New updates are available on GitHub![/bold yellow] (Commit: {remote_hash})'
        )
        console.print('=' * 55)

        answer = input('\nUpdate Orakul Archivist right now? (y/n): ').strip().lower()
        
        if answer == 'y':
            print('\n[+] Starting full core synchronization...')
            success = download_and_extract_full_repo()
            if success:
                print('\n[✓] All files successfully updated! Your baseline and folder configs remain untouched.')
                print('[!] You can now launch the Archivist.')
            else:
                print('\n[!] Error updating files.')
        else:
            print('\n[-] Update cancelled by user.')
    else:
        console.print("[bold green]✅ You have the latest version of Orakul Archivist installed![/bold green]")


if __name__ == '__main__':
    check_for_updates()