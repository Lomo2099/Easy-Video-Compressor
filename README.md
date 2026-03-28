# 🎬 Video Compressor Pro

A modern desktop application to compress large video files to a specific target percentage of their original size. Built with Python and CustomTkinter for a sleek, user-friendly experience.

## ✨ Features
* **Custom Compression:** Use a slider to set your target file size (from 10% to 90%).
* **Modern GUI:** A clean, dark-mode interface that remains responsive during processing.
* **Smart Bitrate Calculation:** Automatically calculates the optimal bitrate to hit your size target.
* **Format Support:** Works with `.mp4`, `.mkv`, `.mov`, and `.avi` files.
* **Threaded Execution:** Compression runs in the background so the app doesn't freeze.

## 🛠️ Prerequisites
To run this tool, you need:
1. **Python 3.8+**
2. **FFmpeg:** (Crucial for video encoding)
   - **Windows:** Download from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add to your PATH.
   - **Linux:** `sudo apt install ffmpeg` or `sudo pacman -S ffmpeg`.

## 🚀 Getting Started

1. **Clone the repo:**
   ```bash
   git clone [https://github.com/YourUsername/Video-Compressor-Pro.git](https://github.com/YourUsername/Video-Compressor-Pro.git)
   cd Video-Compressor-Pro
