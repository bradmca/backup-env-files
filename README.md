# 🛡️ EnvGuard: The Ultimate .env Backup Utility 🚀

Welcome to **EnvGuard**! Never lose a precious environment variable or database secret again. 

Whether you're juggling fifty side projects, surviving daily system reboots, or you just love complete peace of mind, this script is your trusty sidekick for rescuing those elusive `.env` files from the depths of your hard drive. 🦸‍♂️💻

## ✨ What does it do?

EnvGuard doesn't just copy files—it embarks on a heroic, recursive journey traversing your directories, locating **ANY** file starting with `.env` (we're talking `.env`, `.env.local`, `.env.production`, you name it!), and securely backing them up to a unified destination. 

But wait, there's more! 🎩✨ It recreates the **exact folder tree structure** in the backup directory, so you'll always know exactly where those secrets originally came from.

## 🌟 Key Features

- **🌳 Perfect Tree Preservation**: Mirrors your source directory's structure perfectly inside the backup folder.
- **🛡️ Bulletproof Scanning**: Laughs in the face of permission errors and carries on scanning without crashing.
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
1. Scan your sweeping **`C:\`** drive. (Hold onto your hats! 🎩💨)
2. Carefully place all salvaged `.env` files into a neatly organized **`C:\env_backup`** folder.

### 🎛️ Taking Control (Custom Flags)

Want to target specific project folders instead of the whole drive? Use the parameters!

```powershell
python backup_env_files.py --source "C:\Users\Brad\CascadeProjects" --backup "D:\MySecureBackups\EnvVault"
```

#### The Arguments:
- `--source`: Where should the search begin? (Default: `C:\`)
- `--backup`: Where should the rescued files be stored? (Default: `C:\env_backup`)

## 💡 Pro Tips

- **Patience is a Virtue**: If you're scanning your entire `C:\` drive top-to-bottom, grab a coffee ☕. It might take a few minutes to weave through the Windows OS labyrinth.
- **Permission Errors Are Normal**: When scanning root drives, Windows will deny access to restricted system folders. EnvGuard handles these silently and gracefully, logging them in the final error count, but it won't stop the backup.

---
*Built to keep your developer secrets safe, sound, and fully backed up! 🎉*
