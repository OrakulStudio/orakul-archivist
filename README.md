# 👁️ ORAKUL ARCHIVIST - System Watchdog TUI v1.1
> **Developed by Orakul Studio**
> *A low level system monitor for real time tracking of file and directory changes.*

v1.1 Release Notes: A major update to the Orakul Archivist interface. We have transitioned to a strict, monochrome TUI design free of garish colors and emojis incorporated clean `box.ROUNDED` borders, and refined the readability of tables for use within semi-transparent terminal windows. Performance speeds and the microsecond-level precision of metadata verification remain unchanged.
(26.10.2026)
---

## 🚀 About the Program

**ORAKUL ARCHIVIST** is an ultra fast console based TUI (Text User Interface) tool designed for the instant tracking of any changes additions, modifications, or deletions within large-scale projects, datasets, code repositories, and directories containing AI models.

Unlike standard monitoring utilities, the Archivist is engineered to handle massive structures comprising **over 140,000 files**. A full scan of the file system takes just **0.15 seconds**, thanks to direct, low-level Windows C-API calls (`os.scandir`) and optimized `STAT` hashes.

---

## ⚡ Key Features

* **Reactive Speed ​​(`os.scandir` + `STAT`):** Indexes 140,000+ files in a fraction of a second, with minimal impact on memory or CPU usage.
* **Comprehensive Tracking:** Precisely monitors the creation, modification, and deletion of both **individual files** and **entire directories**.
* **Intuitive Navigation (`↑` / `↓`):** Large lists of changes remain accessible scroll through them easily using your keyboard's arrow keys.
* **Automated Text Reports:** Every detected change, along with its timestamp, is logged to the `archivist_last_changes.txt` file. * **Bilingual Interface (RU / EN):** Switch languages ​​instantly with a single click, directly from the console.

---

## ⚠️ CRITICAL EXIT RULE!

> ### 🛑 ALWAYS EXIT THE PROGRAM BY PRESSING THE **[Q]** KEY!
>
> 1. When you exit using the **`[Q]`** key, the utility **automatically generates a complete text report** of all changes including a precise timestamp and saves it to a file named `archivist_last_changes.txt`. It then updates the system snapshot to serve as the new, perfect baseline. The next time you launch the program, you’ll start with a clean slate!
> 2. If you close the window by clicking the **`[X]`** button, the report **will NOT be saved**. Furthermore, previous changes will remain in the log, which can cause confusion the next time you run the program.
>
> **Make it a habit to close the utility exclusively by using the `[Q]` key!**

---

## 🎮 Hotkeys and Controls

| Key | Action | Description |
| :--- | :--- | :--- |
| **`[Enter]`** / **`[Space]`** | **Scan** | Trigger an immediate, on-the-fly disk scan. |
| **`[↑]`** / **`[↓]`** | **Scroll** | Scroll through the list of modified files. |
| **`[+]`** | **Add Folder** | Add a new directory to track (you can also use Drag & Drop into the window). |
| **`[-]`** | **Remove Folder** | Remove a folder from the tracking list by its index number. |
| **`[R]`** | **Reset Baseline** | Sets the current state of the disk as the new "clean slate" (baseline)  can be done while the program is running, without needing to exit. |
| **`[L]`** | **Change Language** | Instantly switch the interface language (**Russian / English**). |
| **`[Q]`** | **Exit and Save** | **REQUIRED EXIT METHOD!** Saves the report to a file and updates the baseline. |

---

## 🛠️ How the utility's files work

The program creates and uses three main files in its directory:

1. **`archivist_folders.json`**  a settings file that stores the list of all your linked, monitored folders.
2. **`archivist_baseline.json`**  the utility's "memory." It stores a baseline snapshot of all files for comparison.
3. **`archivist_last_changes.txt`**  a text-based history log. Each time you exit using **`[Q]`**, a detailed report is appended here, formatted as follows:
```text
=== ORAKUL ARCHIVIST REPORT [2026-10-24 22:15:30] ===

--- NEW ITEMS (2) ---
[+] D:\AI_Models\TEST.txt (Modified: 2026-10-24 22:14:02)
[+] D:\AI_Models\New Folder\

--- MODIFIED ITEMS (1) ---
[~] D:\AI_Models\ai-toolkit\config.py (Modified: 2026-10-24 22:15:10)

--- DELETED ITEMS (1) ---
[-] D:\AI_Models\old_script.txt
```

---

## 🚀 Quick Start Guide

1. **Launch:** Run the `run_archivist.bat` file.
2. **Add Folders:** If the list of tracked folders is empty, press **`[+]`**, drag a folder from Windows Explorer into the console window, and press **`Enter`**.
3. **Initial Snapshot:** In a fraction of a second, the program will create a baseline reference (`archivist_baseline.json`) and display the message: `✨ All clear. No file changes detected!`.
4. **Work:** Go about your tasks modify code, update models, edit text files, or create/delete folders.
5. **Check:** Press **`[Enter]`** or the **`[Spacebar]`** to perform a scan. Any recent changes will appear on the screen instantly. Use the **`[↑]`** / **`[↓]`** arrow keys to navigate the list.
6. **Exit:** Press **`[Q]`**. The utility will automatically write a log to `archivist_last_changes.txt` and save the current state for your next session.

---

## 🔄 Updates (1-Click Updater)

The utility includes an update script: **`update_archivist.bat`**.

Whenever a new version is released (for example, v1.1, which adds highlighting for the active row during scrolling), simply run `update_archivist.bat`. It will fetch the latest code from the official repository **without losing your settings or linked folders**.

---

---
🎬 Video & ORAKUL ARCHIVIST

[ORAKUL ARCHIVIST](https://youtube.com/shorts/etRVLriOiYI?si=kJnjBFQIxhAcrhcV)

*▶️ Click the player above to watch the full video on YouTube*

---


## 📜 License

This project is licensed under the **MIT License**  free for personal and commercial use. See the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://members.opensource.org/user/roman-nykonov) file for details.

*Created by Orakul Studio | 2026*
