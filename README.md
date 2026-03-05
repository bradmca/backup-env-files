# 🛡️ EnvGuard: The Ultimate .env Backup Utility 🚀

Welcome to **EnvGuard**! Never lose a precious environment variable or database secret again. 

Whether you're juggling fifty side projects, surviving daily system reboots, or you just love complete peace of mind, this script is your trusty sidekick for rescuing those elusive `.env` files from the depths of your hard drive. 🦸‍♂️💻

## ✨ What does it do?

EnvGuard doesn't just copy files—it embarks on a heroic, recursive journey traversing **every local drive on your machine concurrently** via multithreading, locating **ANY** file starting with `.env` (we're talking `.env`, `.env.local`, `.env.production`, you name it!), and securely backing them up into a single, dated **zip archive**. 

But wait, there's more! 🎩✨ Inside the zip archive, the files are intelligently organized by your **machine's hostname**, followed by the **drive letter**, and recreates the **exact folder tree structure**, so you'll always know precisely where those secrets originally came from.

## 🌟 Key Features

- **🚀 Multithreaded Scanning**: Dispatches an independent thread for every local drive (C:\, D:\, etc.) to scan your system at lightning speed.
- **💻 Hostname-Aware Separation**: Backups are automatically sorted into folders matching your machine's unique hostname. 
- **🌳 Perfect Tree Preservation**: Mirrors your source directory's structure perfectly inside the backup archive (e.g., `MachineName/C/Users/Brad/...`).
- **📦 Auto-Archiving**: Automatically packages the organized backup into a dated zip archive (`env-backup-YYYY-MM-DD.zip`) for easy storage and sharing.
- **🛡️ Bulletproof Execution**: Laughs in the face of permission errors and carries on scanning without crashing.
- **🤖 Smart & Safe**: Refuses to trigger infinite loops (automatically detects and skips its own backup destination).
- **⚡ Lightweight**: Written in pure, dependency-free Python. 🐍 Just script and go!

## 🛠️ Getting Started

### Prerequisites
All you need is **Python 3.x** installed on your machine. No pip installs, no virtual environments.

### 🏃‍♂️ Running the Magic

Open your terminal, navigate to the folder containing the script, and run:

```powershell
python backup_env_files.py
```

By default, it will:
1. Identify all accessible local drives (e.g., `C:\`, `D:\`).
2. Spawn a thread for each drive. (Hold onto your hats! 🎩💨)
3. Compress all salvaged `.env` files into a single zip archive named **`C:\env_backup\env-backup-YYYY-MM-DD.zip`**.

### 🎛️ Taking Control (Custom Flags)

Want to target a specific backup folder somewhere else? Use the `--backup` parameter!

```powershell
python backup_env_files.py --backup "D:\MySecureBackups\EnvVault"
```

#### The Arguments:
- `--backup`: Where should the backup zip archive be stored? (Default: `C:\env_backup`)

## 💡 Pro Tips

- **Patience is a Virtue**: Even with multithreading, if you have massively packed drives, grab a coffee ☕. It might take a few minutes for the threads to weave through the Windows OS labyrinths.
- **Permission Errors Are Normal**: When scanning root drives, Windows will naturally deny access to restricted system folders. EnvGuard handles these silently and gracefully, logging them in the final error count, but it won't stop the backup.

---
*Built to keep your developer secrets safe, sound, and fully backed up! 🎉*
