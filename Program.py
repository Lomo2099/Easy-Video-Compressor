import customtkinter as ctk
import os
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import filedialog, messagebox
from moviepy import VideoFileClip

# Set the appearance theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class VideoCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Media Compressor Pro - Batch Video Compressor")
        self.geometry("620x660")
        self.minsize(560, 520)

        # State tracking
        self.selected_files = []  # List of selected file paths
        self.file_widgets = {}    # Path -> dict of row widgets
        self.is_compressing = False
        self.ui_queue = queue.Queue()

        # Start periodic UI queue processor for thread-safe UI updates
        self.after(50, self._process_ui_queue)

        # --- UI Header ---
        self.header_label = ctk.CTkLabel(
            self, text="Batch Video Compressor", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.pack(pady=(16, 4))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Upload multiple videos at once and compress them simultaneously",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.subtitle_label.pack(pady=(0, 10))

        # --- File Selection Controls ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=5, padx=20, fill="x")

        self.select_btn = ctk.CTkButton(
            self.controls_frame,
            text="Select Video Files",
            command=self.browse_files,
            width=160,
        )
        self.select_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="Clear All",
            command=self.clear_files,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=90,
        )
        self.clear_btn.pack(side="left")

        self.count_label = ctk.CTkLabel(
            self.controls_frame, text="0 videos selected", text_color="gray"
        )
        self.count_label.pack(side="right")

        # --- Scrollable File List ---
        self.files_scroll_frame = ctk.CTkScrollableFrame(
            self, height=200, label_text="Selected Video Queue"
        )
        self.files_scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.empty_label = ctk.CTkLabel(
            self.files_scroll_frame,
            text="No files selected yet.\nClick 'Select Video Files' to choose one or more videos.",
            text_color="gray",
            justify="center",
        )
        self.empty_label.pack(pady=50)

        # --- Compression Slider ---
        self.slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.slider_frame.pack(pady=(10, 5), padx=20, fill="x")

        self.slider_label = ctk.CTkLabel(
            self.slider_frame,
            text="Target Size: 50%",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.slider_label.pack(pady=(0, 5))

        self.pct_slider = ctk.CTkSlider(
            self.slider_frame, from_=10, to=90, command=self.update_slider_label
        )
        self.pct_slider.set(50)
        self.pct_slider.pack(fill="x", padx=10)

        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(15, 5), padx=20)

        # --- Compress Button ---
        self.compress_btn = ctk.CTkButton(
            self,
            text="Start Parallel Compression",
            command=self.start_compression_thread,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42,
        )
        self.compress_btn.pack(pady=(10, 5), padx=20, fill="x")

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.pack(pady=(5, 15))

    def post_to_ui(self, fn, *args, **kwargs):
        """Thread-safe dispatch to the main Tkinter thread."""
        self.ui_queue.put((fn, args, kwargs))

    def _process_ui_queue(self):
        """Processes queued UI updates safely on the Tkinter main thread."""
        try:
            while not self.ui_queue.empty():
                fn, args, kwargs = self.ui_queue.get_nowait()
                try:
                    fn(*args, **kwargs)
                except Exception as e:
                    print(f"Error executing UI task: {e}")
        finally:
            self.after(50, self._process_ui_queue)

    def browse_files(self):
        """Allows selecting multiple video files at once."""
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.mov *.avi *.webm *.flv *.m4v *.wmv"),
                ("All files", "*.*"),
            ],
        )
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
            self.refresh_file_list()

    def remove_file(self, file_path):
        """Removes a single file from the selected list."""
        if self.is_compressing:
            return
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
        self.refresh_file_list()

    def clear_files(self):
        """Clears all selected files."""
        if self.is_compressing:
            return
        self.selected_files.clear()
        self.refresh_file_list()

    def refresh_file_list(self):
        """Re-renders the scrollable list of selected files."""
        for widget in self.files_scroll_frame.winfo_children():
            widget.destroy()
        self.file_widgets.clear()

        if not self.selected_files:
            self.empty_label = ctk.CTkLabel(
                self.files_scroll_frame,
                text="No files selected yet.\nClick 'Select Video Files' to choose one or more videos.",
                text_color="gray",
                justify="center",
            )
            self.empty_label.pack(pady=50)
            self.count_label.configure(text="0 videos selected")
            return

        count = len(self.selected_files)
        self.count_label.configure(text=f"{count} video{'s' if count > 1 else ''} selected")

        for file_path in self.selected_files:
            row = ctk.CTkFrame(self.files_scroll_frame, fg_color=("gray85", "gray20"))
            row.pack(fill="x", pady=3, padx=5)

            base_name = os.path.basename(file_path)
            try:
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
            except Exception:
                size_str = "Unknown"

            name_label = ctk.CTkLabel(
                row,
                text=f"{base_name} ({size_str})",
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
            )
            name_label.pack(side="left", padx=10, pady=6, fill="x", expand=True)

            status_label = ctk.CTkLabel(
                row, text="Ready", text_color="gray", font=ctk.CTkFont(size=11)
            )
            status_label.pack(side="left", padx=10)

            remove_btn = ctk.CTkButton(
                row,
                text="✕",
                width=26,
                height=26,
                fg_color="transparent",
                text_color="#e74c3c",
                hover_color=("gray75", "gray30"),
                command=lambda p=file_path: self.remove_file(p),
            )
            remove_btn.pack(side="right", padx=5)

            self.file_widgets[file_path] = {
                "row": row,
                "status_label": status_label,
                "remove_btn": remove_btn,
            }

    def update_slider_label(self, value):
        self.slider_label.configure(text=f"Target Size: {int(value)}%")

    def start_compression_thread(self):
        """Validates selection and initiates concurrent compression."""
        if self.is_compressing:
            return

        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select at least one video file first!")
            return

        percentage = self.pct_slider.get()
        self.is_compressing = True

        # Lock UI inputs
        self.select_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        self.compress_btn.configure(state="disabled")
        self.pct_slider.configure(state="disabled")
        for w in self.file_widgets.values():
            w["remove_btn"].configure(state="disabled")

        self.progress_bar.set(0)
        total_count = len(self.selected_files)
        self.status_label.configure(
            text=f"Compressing {total_count} video{'s' if total_count > 1 else ''} simultaneously...",
            text_color="#f39c12",
        )

        # Run parallel compression in a dedicated supervisor thread to keep UI fluid
        thread = threading.Thread(
            target=self._run_parallel_compression,
            args=(list(self.selected_files), percentage),
            daemon=True,
        )
        thread.start()

    def _run_parallel_compression(self, files, percentage):
        """Processes all selected videos concurrently using ThreadPoolExecutor."""
        total_files = len(files)
        completed_count = 0
        results = []
        lock = threading.Lock()

        # Run videos simultaneously (up to 8 parallel workers)
        max_workers = min(total_files, 8)

        def worker(file_path):
            nonlocal completed_count

            # Indicate that this specific file started compressing
            self.post_to_ui(self._update_file_status, file_path, "Compressing...", "#f39c12")

            result = self.compress_single_video(file_path, percentage)

            with lock:
                completed_count += 1
                current_progress = completed_count / total_files
                results.append(result)

                if result["success"]:
                    msg = f"Done ({result['original_mb']:.1f}MB → {result['new_mb']:.1f}MB, -{result['savings_pct']:.0f}%)"
                    color = "#2ecc71"
                else:
                    msg = f"Failed: {result['error']}"
                    color = "#e74c3c"

                self.post_to_ui(
                    self._on_video_completed,
                    file_path,
                    msg,
                    color,
                    current_progress,
                    completed_count,
                    total_files,
                )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker, fp) for fp in files]
            for f in as_completed(futures):
                pass

        self.post_to_ui(self._finish_batch, results)

    def compress_single_video(self, input_path, percentage):
        """Compresses an individual video based on the percentage target size."""
        clip = None
        try:
            if not os.path.isfile(input_path):
                return {"path": input_path, "success": False, "error": "File not found"}

            original_size = os.path.getsize(input_path)
            clip = VideoFileClip(input_path)

            duration = clip.duration if clip.duration and clip.duration > 0 else 1.0
            reduction_factor = percentage / 100.0
            target_bitrate = (original_size * 8 * reduction_factor) / duration
            # Guard against invalid or extremely low bitrates
            target_bitrate = max(100_000, int(target_bitrate))

            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_{int(percentage)}pct{file_ext}"
            if output_path == input_path:
                output_path = f"{file_name}_{int(percentage)}pct_compressed{file_ext}"

            clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                bitrate=f"{target_bitrate}",
                logger=None,
            )

            clip.close()
            clip = None

            new_size = os.path.getsize(output_path)
            savings_pct = max(0.0, (1.0 - (new_size / original_size)) * 100) if original_size > 0 else 0.0

            return {
                "path": input_path,
                "output_path": output_path,
                "success": True,
                "original_bytes": original_size,
                "new_bytes": new_size,
                "original_mb": original_size / (1024 * 1024),
                "new_mb": new_size / (1024 * 1024),
                "savings_pct": savings_pct,
                "error": None,
            }
        except Exception as e:
            return {
                "path": input_path,
                "success": False,
                "error": str(e),
                "original_bytes": 0,
                "new_bytes": 0,
            }
        finally:
            if clip is not None:
                try:
                    clip.close()
                except Exception:
                    pass

    def _update_file_status(self, file_path, text, color):
        """Updates the status text and color for a specific file row."""
        if file_path in self.file_widgets:
            self.file_widgets[file_path]["status_label"].configure(text=text, text_color=color)

    def _on_video_completed(self, file_path, status_text, color, progress, completed, total):
        """Updates UI as each video finishes."""
        self._update_file_status(file_path, status_text, color)
        self.progress_bar.set(progress)
        self.status_label.configure(
            text=f"Compressing videos: {completed}/{total} completed",
            text_color="#f39c12",
        )

    def _finish_batch(self, results):
        """Resets controls and displays compression summary dialog."""
        self.is_compressing = False
        self.select_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")
        self.compress_btn.configure(state="normal")
        self.pct_slider.configure(state="normal")
        for w in self.file_widgets.values():
            w["remove_btn"].configure(state="normal")

        self.progress_bar.set(1.0)

        successes = [r for r in results if r["success"]]
        failures = [r for r in results if not r["success"]]

        total_orig = sum(r.get("original_bytes", 0) for r in successes)
        total_new = sum(r.get("new_bytes", 0) for r in successes)
        total_orig_mb = total_orig / (1024 * 1024)
        total_new_mb = total_new / (1024 * 1024)
        saved_mb = max(0.0, total_orig_mb - total_new_mb)
        saved_pct = ((saved_mb / total_orig_mb) * 100) if total_orig_mb > 0 else 0.0

        if not failures:
            status_msg = f"Completed all {len(successes)} video(s) successfully!"
            status_color = "#2ecc71"
            summary_title = "Compression Complete"
            summary_body = (
                f"Successfully compressed {len(successes)} video(s) simultaneously.\n\n"
                f"Original Size: {total_orig_mb:.2f} MB\n"
                f"New Size: {total_new_mb:.2f} MB\n"
                f"Space Saved: {saved_mb:.2f} MB ({saved_pct:.1f}%)"
            )
            messagebox.showinfo(summary_title, summary_body)
        else:
            status_msg = f"Finished: {len(successes)} succeeded, {len(failures)} failed."
            status_color = "#e74c3c" if not successes else "#f39c12"
            summary_title = "Compression Finished (with issues)"
            fail_details = "\n".join(f"- {os.path.basename(r['path'])}: {r['error']}" for r in failures)
            summary_body = (
                f"Processed {len(results)} video(s).\n"
                f"Successful: {len(successes)}\n"
                f"Failed: {len(failures)}\n\n"
                f"Space Saved: {saved_mb:.2f} MB\n\n"
                f"Errors:\n{fail_details}"
            )
            messagebox.showwarning(summary_title, summary_body)

        self.status_label.configure(text=status_msg, text_color=status_color)


if __name__ == "__main__":
    app = VideoCompressorApp()
    app.mainloop()
