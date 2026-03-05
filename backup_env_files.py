import os
import shutil
from pathlib import Path
import argparse
import time

def backup_env_files(source_dir: str, backup_dir: str):
    """
    Recursively browses all folders from source_dir, looks for files starting with '.env',
    and copies them to backup_dir while preserving the folder tree structure.
    """
    source_path = Path(source_dir).resolve()
    backup_path = Path(backup_dir).resolve()

    if source_path == backup_path or backup_path.is_relative_to(source_path):
        print(f"Warning: Backup directory '{backup_path}' is inside the source directory.")
        print("The script will skip the backup directory to avoid infinite loops.")

    print(f"Starting backup...")
    print(f"Source: {source_path}")
    print(f"Backup: {backup_path}")
    print("-" * 40)

    copied_count = 0
    error_count = 0
    start_time = time.time()

    # os.walk is used for traversing the directory tree robustly
    for root, dirs, files in os.walk(source_path):
        # Prevent searching inside the backup directory if it's within the source directory
        try:
            current_root = Path(root).resolve()
            if backup_path == current_root or backup_path in current_root.parents:
                dirs[:] = [] # Clear the dirs to avoid traversing further into the backup path
                continue
        except Exception:
            pass # Ignore issues resolving paths and just continue

        for file in files:
            # Check if the file starts with '.env' (like .env, .env.local, .env.development, etc.)
            if file.startswith('.env'):
                source_file_path = Path(root) / file
                
                try:
                    # Calculate the path relative to the source directory
                    # Example: if source=C:\ and file=C:\project\.env, relative=project\.env
                    relative_path = source_file_path.relative_to(source_path)

                    target_file_path = backup_path / relative_path
                    
                    # Create target directory structure
                    target_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy the file with metadata (permissions, timestamps)
                    shutil.copy2(source_file_path, target_file_path)
                    print(f"Backed up: {source_file_path} -> {target_file_path}")
                    copied_count += 1
                    
                except PermissionError:
                    print(f"Permission denied: {source_file_path}")
                    error_count += 1
                except ValueError:
                    print(f"Could not resolve relative path for: {source_file_path}")
                    error_count += 1
                except Exception as e:
                    print(f"Error copying {source_file_path}: {e}")
                    error_count += 1

    elapsed_time = time.time() - start_time
    print("-" * 40)
    print("Backup complete!")
    print(f"Files copied: {copied_count}")
    print(f"Errors: {error_count}")
    print(f"Time taken: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    # Set up command line argument parsing for flexible usage
    parser = argparse.ArgumentParser(
        description="Backup all .env files from a source directory to a backup directory, preserving the folder structure.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--source", 
        default="C:\\\\", 
        help="The source directory to scan (e.g., C:\\\\)"
    )
    parser.add_argument(
        "--backup", 
        default=r"C:\env_backup", 
        help="The destination directory where the backup tree will be created"
    )
    
    args = parser.parse_args()
    
    # Ensure backup directory exists before starting
    try:
        os.makedirs(args.backup, exist_ok=True)
    except Exception as e:
        print(f"Failed to create backup directory {args.backup}: {e}")
        exit(1)
    
    backup_env_files(args.source, args.backup)
