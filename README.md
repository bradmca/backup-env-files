# 🛡️ EnvGuard: The Ultimate .env & Dev Config Backup Utility 🚀

Welcome to **EnvGuard**! Never lose a precious environment variable, database secret, or development configuration file again. 

Whether you're juggling fifty side projects, surviving daily system reboots, or you just love complete peace of mind, this script is your trusty sidekick for rescuing those elusive `.env` and development configuration `.json` files from the depths of your hard drive. 🦸‍♂️💻

## ✨ What does it do?

EnvGuard doesn't just copy files—it embarks on a heroic, recursive journey traversing **every local drive on your machine concurrently** via multithreading, locating:
- **Environment files**: Any file starting with `.env` (we're talking `.env`, `.env.local`, `.env.production`, etc.)
- **Development config files**: Any `.json` file with `mcp`, `settings`, or `config` in the name (e.g. `mcp_config.json`, `settings.json`, `tsconfig.json`, `launchsettings.json`), project manifests (`package.json`, `composer.json`, `deno.json`), IDE configs (`launch.json`, `tasks.json`), and tool dotfiles (e.g. `.eslintrc.json`, `.prettierrc.json`).

Inside the zip archive, the files are intelligently organized by your **machine's hostname**, followed by the **drive letter**, and recreates the **exact folder tree structure**, so you'll always know precisely where those secrets and configurations originally came from.

### ⚙️ How It Works Under the Hood (Two-Stage Execution)

1. **Real-Time Staging (As It Goes):** As worker threads scan your drives, any matching `.env` or config `.json` file found is **copied immediately** into a temporary staging folder on disk, recreating the folder hierarchy in real-time with sanitized timestamps.
2. **Final Compression & Cleanup (At the End):** Once all scanning threads finish, the script safely packages the staged directory into a dated `.zip` archive (e.g. `P:\Business\env_backup\env-backup-YYYY-MM-DD.zip`), shows live compression progress, and cleans up the staging files.

## 🌟 Key Features

- **🚀 Multithreaded Scanning**: Dispatches independent worker threads across all local drives (C:\, D:\, etc.) to scan your system at lightning speed.
- **🎯 Targeted Dev Config Filtering**: Intelligently matches essential configs (`mcp`, `settings`, `config`, `package.json`, `launch.json`, `.eslintrc.json`, etc.) without bloating your backup with lockfiles or cache artifacts.
- **⚡ Real-Time Staging**: Copies files to a temporary staging area immediately as they are discovered during the scan.
- **💻 Hostname-Aware Separation**: Backups are automatically sorted into folders matching your machine's unique hostname. 
- **🌳 Perfect Tree Preservation**: Mirrors your source directory's structure perfectly inside the backup archive (e.g., `MachineName/C/Users/Brad/...`).
- **📦 Auto-Archiving with Zip64**: Automatically packages the organized backup into a dated zip archive (`env-backup-YYYY-MM-DD.zip`), handling pre-1980 timestamps safely and supporting massive file counts.
- **🛡️ Bulletproof Execution**: Laughs in the face of permission errors and carries on scanning without crashing.
- **🚫 Smart Directory Exclusions**: Automatically skips OS system folders (`C:\Windows`, `ProgramData`), user system caches (`AppData`, `Temp`, `tmp`), recycle bins (`$Recycle.Bin`), heavy dependency trees (`node_modules`), source control metadata (`.git`), virtual environments (`venv`, `.venv`), and build artifacts (`dist`, `build`, `.next`, `.cache`) to dramatically speed up scanning.
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
2. Spawn worker threads across top-level locations.
3. Copy `.env` and `.json` files into a temporary staging folder in real-time as they are found.
4. Compress all salvaged files into a single zip archive named **`P:\Business\env_backup\env-backup-YYYY-MM-DD.zip`** and clean up temporary files.

### 🎛️ Taking Control (Custom Flags)

Want to target a specific backup folder somewhere else? Use the `--backup` parameter!

```powershell
python backup_env_files.py --backup "D:\MySecureBackups\EnvVault"
```

#### The Arguments:
- `--backup`: Where should the backup zip archive be stored? (Default: `P:\Business\env_backup`)

## 💡 Pro Tips

- **Patience is a Virtue**: Even with multithreading, if you have massively packed drives, grab a coffee ☕. It might take a few minutes for the threads to weave through the Windows OS labyrinths.
- **Permission Errors Are Normal**: When scanning root drives, Windows will naturally deny access to restricted system folders. EnvGuard handles these silently and gracefully, logging them in the final error count, but it won't stop the backup.

---
*Built to keep your developer secrets safe, sound, and fully backed up! 🎉*
