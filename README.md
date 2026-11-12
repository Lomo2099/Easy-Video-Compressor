# 🎬 Video Compressor Pro

A modern desktop application to compress large video files to a specific target percentage of their original size. Built with Python and CustomTkinter for a sleek, user-friendly experience. Now supports **multi-video batch selection** and **simultaneous parallel compression**!

## ✨ Features
* **Multi-Video Batch Upload:** Select multiple video files at once using the file browser.
* **Simultaneous Parallel Compression:** Compresses all selected videos concurrently in background worker threads without freezing the UI.
* **Per-Video Queue & Progress Tracking:** Real-time status indicators for each video (Ready, Compressing, Done with size savings, or Error).
* **Flexible Queue Management:** Add more files to the queue, remove individual files, or clear all.
* **Custom Compression:** Use a slider to set your target file size (from 10% to 90%).
* **Modern GUI:** A clean CustomTkinter interface with dark/light mode support.
* **Smart Bitrate Calculation:** Automatically calculates the optimal bitrate to hit your size target based on duration and original size.
* **Format Support:** Works with `.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.flv`, and `.m4v` files.
* **Thread-Safe Architecture:** Background worker threads safely communicate with the GUI via event queues.

## 🛠️ Prerequisites
To run this tool, you need:
1. **Python 3.12+**
2. **FFmpeg:** (Crucial for video encoding)
   - **Windows:** Download from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add to your PATH.
   - **Linux:** `sudo apt install ffmpeg` or `sudo pacman -S ffmpeg`.
   - **Mac OS:** `brew install ffmpeg`

## 🚀 Getting Started

1. **Clone the repo:**
   ```bash
   git clone https://github.com/YourUsername/Video-Compressor-Pro.git
   cd Video-Compressor-Pro
   ```

2. **Install Python dependencies:**
   ```bash
   pip install customtkinter moviepy
   ```

3. **Run the application:**
   ```bash
   python Program.py
   ```
