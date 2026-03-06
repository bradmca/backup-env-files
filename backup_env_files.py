import os
import shutil
import socket
import string
import time
import argparse
import threading
import tempfile
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def status_indicator(stop_event: threading.Event, counters: dict, lock: threading.Lock):
    """Background thread that prints a status indicator."""
    spinner = ['-', '\\', '|', '/']
    idx = 0
    while not stop_event.is_set():
        with lock:
            # We use \r to return to the beginning of the line, and spaces to clear the old line
            stats = f"Dirs scanned: {counters['scanned_dirs']} | Files scanned: {counters['scanned_files']} | Copied: {counters['copied']} | Errors: {counters['errors']}"
            print(f"\r{spinner[idx % len(spinner)]} {stats}".ljust(80), end="", flush=True)
        idx += 1
        time.sleep(0.1)
    
    # Clear the status line when done
    with lock:
        print("\r" + " " * 100 + "\r", end="", flush=True)


def get_local_drives():
    """Returns a list of local drive paths (e.g., ['C:\\', 'D:\\'])."""
    drives = []
    # Check all possible drive letters
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def _copy_env_file(source_file_path: Path, drive_root_path: Path, base_target_backup_path: Path, drive_folder_name: str, lock: threading.Lock, counters: dict):
    try:
        relative_path = source_file_path.relative_to(drive_root_path)
        target_file_path = base_target_backup_path / relative_path
        
        target_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file_path, target_file_path)
        
        with lock:
            print(f"\r[{drive_folder_name} Drive] Backed up: {source_file_path} -> {target_file_path}".ljust(80))
            counters['copied'] += 1
    
    except PermissionError:
        with lock:
            print(f"\r[{drive_folder_name} Drive] Permission denied: {source_file_path}".ljust(80))
            counters['errors'] += 1
    except ValueError:
        with lock:
            print(f"\r[{drive_folder_name} Drive] Could not resolve relative path: {source_file_path}".ljust(80))
            counters['errors'] += 1
    except Exception as e:
        with lock:
            print(f"\r[{drive_folder_name} Drive] Error copying {source_file_path}: {e}".ljust(80))
            counters['errors'] += 1

def backup_path_task(target_path_str: str, drive_path_str: str, base_backup_dir: str, machine_name: str, lock: threading.Lock, counters: dict):
    """
    Scans a specific directory or file and backs up .env files.
    """
    try:
        target_path = Path(target_path_str).resolve()
        drive_root_path = Path(drive_path_str).resolve()
    except Exception:
        return # Skip if we can't resolve the path
    
    drive_folder_name = drive_root_path.drive.replace(":", "") 
    if not drive_folder_name:
        # Fallback if no drive letter is found (rare on Windows)
        drive_folder_name = drive_root_path.name or "Root"
        
    base_target_backup_path = Path(base_backup_dir).resolve() / machine_name / drive_folder_name
    
    # Avoid scanning the backup directory itself
    global_backup_path = Path(base_backup_dir).resolve()

    local_dirs_scanned = 0
    local_files_scanned = 0

    try:
        if target_path.is_file():
            if target_path.name.startswith('.env'):
                _copy_env_file(target_path, drive_root_path, base_target_backup_path, drive_folder_name, lock, counters)
            with lock:
                counters['scanned_files'] += 1
            return
    except Exception:
        pass # Ignore permission or resolution errors on is_file

    for root, dirs, files in os.walk(target_path):
        local_dirs_scanned += 1
        local_files_scanned += len(files)
        
        # Update global counters occasionally to minimize lock contention
        if local_dirs_scanned % 100 == 0:
            with lock:
                counters['scanned_dirs'] += local_dirs_scanned
                counters['scanned_files'] += local_files_scanned
            local_dirs_scanned = 0
            local_files_scanned = 0

        try:
            current_root = Path(root).resolve()
            # If the current subfolder is the backup directory or inside it, skip it
            if global_backup_path == current_root or global_backup_path in current_root.parents:
                dirs[:] = []  # Prevents os.walk from entering this directory
                continue
        except Exception:
            pass # Ignore resolution errors and keep going

        for file in files:
            if file.startswith('.env'):
                source_file_path = Path(root) / file
                _copy_env_file(source_file_path, drive_root_path, base_target_backup_path, drive_folder_name, lock, counters)

    # Add any remaining local counters to global counters when loop completes
    with lock:
        counters['scanned_dirs'] += local_dirs_scanned
        counters['scanned_files'] += local_files_scanned

def start_multi_drive_backup(backup_dir: str):
    machine_name = socket.gethostname()
    drives = get_local_drives()
    
    print("-" * 50)
    print("Starting Multi-threaded EnvGuard Backup...")
    print(f"Machine Name: {machine_name}")
    print(f"Local Drives found: {drives}")
    print(f"Temporary Staging Directory: {Path(backup_dir).resolve()}")
    print("-" * 50)
    
    counters = {'copied': 0, 'errors': 0, 'scanned_dirs': 0, 'scanned_files': 0}
    lock = threading.Lock()  # Synchronize print statements and counters modification
    stop_event = threading.Event()
    start_time = time.time()
    
    # Start status indicator thread
    status_thread = threading.Thread(target=status_indicator, args=(stop_event, counters, lock), daemon=True)
    status_thread.start()
    
    # To maximize thread usage on high core-count machines, we submit top-level items of each drive as separate tasks
    tasks = []
    for drive in drives:
        try:
            for entry in os.scandir(drive):
                tasks.append((entry.path, drive))
        except PermissionError:
            print(f"Permission denied scanning root of drive {drive}")
        except Exception as e:
            print(f"Could not scan root of drive {drive}: {e}")

    # Set up ThreadPoolExecutor with a larger max_workers (up to 40 for 20-core systems)
    max_threads = min(40, (os.cpu_count() or 1) * 2) 
    print(f"Submitting {len(tasks)} top-level filesystem locations to {max_threads} worker threads...")
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for target_path, drive_path in tasks:
            futures.append(executor.submit(backup_path_task, target_path, drive_path, backup_dir, machine_name, lock, counters))
            
        for future in as_completed(futures):
            try:
                # Process exceptions within the threads if they bubbled up
                future.result()
            except Exception as e:
                with lock:
                    print(f"\r[Main Thread] A child thread encountered an unexpected error: {e}".ljust(80))
                    counters['errors'] += 1

    # Stop status indicator
    stop_event.set()
    status_thread.join()

    elapsed_time = time.time() - start_time
    print("-" * 50)
    print("Backup complete!")
    print(f"Total .env files copied: {counters['copied']}")
    print(f"Total directories scanned: {counters['scanned_dirs']}")
    print(f"Total files scanned: {counters['scanned_files']}")
    print(f"Total errors encountered: {counters['errors']}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backup all .env files from ALL local drives to a zip file named by run date, preserving the folder structure under the machine's hostname.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # The source parameter is removed because it now implicitly scans all local drives
    parser.add_argument(
        "--backup", 
        default="C:\\env_backup", 
        help="The destination directory where the backup zip will be saved"
    )
    
    args = parser.parse_args()
    
    # Ensure backup directory base exists
    try:
        os.makedirs(args.backup, exist_ok=True)
    except Exception as e:
        print(f"Failed to create backup directory {args.backup}: {e}")
        exit(1)
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"env-backup-{date_str}"
    zip_filepath = os.path.join(args.backup, zip_filename)
        
    with tempfile.TemporaryDirectory() as temp_dir:
        start_multi_drive_backup(temp_dir)
        print("-" * 50)
        print(f"Compressing backup to {zip_filepath}.zip...")
        shutil.make_archive(zip_filepath, 'zip', temp_dir)
        print(f"Compression complete! Zip archive located at {zip_filepath}.zip")
