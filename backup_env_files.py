import os
import shutil
import socket
import string
import time
import argparse
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_local_drives():
    """Returns a list of local drive paths (e.g., ['C:\\', 'D:\\'])."""
    drives = []
    # Check all possible drive letters
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def backup_drive(drive_path: str, base_backup_dir: str, machine_name: str, lock: threading.Lock, counters: dict):
    """
    Scans a single drive and backs up .env files.
    """
    source_path = Path(drive_path).resolve()
    
    # We replace the colon to make it a valid folder name, e.g., C:\ -> C
    drive_folder_name = source_path.drive.replace(":", "") 
    if not drive_folder_name:
        # Fallback if no drive letter is found (rare on Windows)
        drive_folder_name = Path(drive_path).name or "Root"
        
    backup_path = Path(base_backup_dir).resolve() / machine_name / drive_folder_name
    
    # Avoid scanning the backup directory itself
    global_backup_path = Path(base_backup_dir).resolve()

    for root, dirs, files in os.walk(source_path):
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
                
                try:
                    # Calculate relative path from the drive root
                    # Using relative_to(source_path) for C:\Users it becomes Users
                    relative_path = source_file_path.relative_to(source_path)
                    target_file_path = backup_path / relative_path
                    
                    target_file_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file_path, target_file_path)
                    
                    with lock:
                        print(f"[{drive_folder_name} Drive] Backed up: {source_file_path} -> {target_file_path}")
                        counters['copied'] += 1
                
                except PermissionError:
                    with lock:
                        print(f"[{drive_folder_name} Drive] Permission denied: {source_file_path}")
                        counters['errors'] += 1
                except ValueError:
                    with lock:
                        print(f"[{drive_folder_name} Drive] Could not resolve relative path: {source_file_path}")
                        counters['errors'] += 1
                except Exception as e:
                    with lock:
                        print(f"[{drive_folder_name} Drive] Error copying {source_file_path}: {e}")
                        counters['errors'] += 1

def start_multi_drive_backup(backup_dir: str):
    machine_name = socket.gethostname()
    drives = get_local_drives()
    
    print("-" * 50)
    print("Starting Multi-threaded EnvGuard Backup...")
    print(f"Machine Name: {machine_name}")
    print(f"Local Drives found: {drives}")
    print(f"Global Backup Destination: {Path(backup_dir).resolve()}")
    print("-" * 50)
    
    counters = {'copied': 0, 'errors': 0}
    lock = threading.Lock()  # Synchronize print statements and counters modification
    start_time = time.time()
    
    # Multithreading: 1 thread per drive to improve I/O latency times
    with ThreadPoolExecutor(max_workers=len(drives)) as executor:
        futures = []
        for drive in drives:
            print(f"Spawning backup thread for drive {drive}...")
            futures.append(executor.submit(backup_drive, drive, backup_dir, machine_name, lock, counters))
            
        for future in as_completed(futures):
            try:
                # Process exceptions within the threads if they bubbled up
                future.result()
            except Exception as e:
                with lock:
                    print(f"[Main Thread] A child thread encountered an unexpected error: {e}")
                    counters['errors'] += 1

    elapsed_time = time.time() - start_time
    print("-" * 50)
    print("Backup complete!")
    print(f"Total .env files copied: {counters['copied']}")
    print(f"Total errors encountered: {counters['errors']}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backup all .env files from ALL local drives to a backup directory, preserving the folder structure under the machine's hostname.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # The source parameter is removed because it now implicitly scans all local drives
    parser.add_argument(
        "--backup", 
        default="C:\\env_backup", 
        help="The destination directory where the backup tree will be created"
    )
    
    args = parser.parse_args()
    
    # Ensure backup directory base exists
    try:
        os.makedirs(args.backup, exist_ok=True)
    except Exception as e:
        print(f"Failed to create backup directory {args.backup}: {e}")
        exit(1)
        
    start_multi_drive_backup(args.backup)
