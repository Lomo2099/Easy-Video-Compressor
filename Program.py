import customtkinter as ctk
import os
import threading
from tkinter import filedialog, messagebox
from moviepy import VideoFileClip

# Set the theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class VideoCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Media Compressor Pro")
        self.geometry("500x450")

        # --- UI Elements ---
        self.label = ctk.CTkLabel(self, text="Video Compressor", font=ctk.CTkFont(size=22, weight="bold"))
        self.label.pack(pady=20)

        # File Selection
        self.file_path = ctk.StringVar()
        self.select_btn = ctk.CTkButton(self, text="Select Video File", command=self.browse_file)
        self.select_btn.pack(pady=10)

        self.path_label = ctk.CTkLabel(self, text="No file selected", wraplength=400, text_color="gray")
        self.path_label.pack(pady=5)

        # Compression Slider
        self.slider_label = ctk.CTkLabel(self, text="Target Size: 50%")
        self.slider_label.pack(pady=(20, 0))
        
        self.pct_slider = ctk.CTkSlider(self, from_=10, to=90, command=self.update_slider_label)
        self.pct_slider.set(50)
        self.pct_slider.pack(pady=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=20)

        # Compress Button
        self.compress_btn = ctk.CTkButton(self, text="Start Compression", command=self.start_compression_thread, fg_color="#2ecc71", hover_color="#27ae60")
        self.compress_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="white")
        self.status_label.pack(pady=5)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mkv *.mov *.avi")])
        if file:
            self.file_path.set(file)
            self.path_label.configure(text=os.path.basename(file), text_color="white")

    def update_slider_label(self, value):
        self.slider_label.configure(text=f"Target Size: {int(value)}%")

    def start_compression_thread(self):
        input_path = self.file_path.get()
        if not input_path:
            messagebox.showwarning("No File", "Please select a video file first!")
            return
        
        percentage = self.pct_slider.get()
        self.compress_btn.configure(state="disabled")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.status_label.configure(text="Compressing... (This may take a while)", text_color="yellow")

        # Run in thread to keep GUI responsive
        thread = threading.Thread(target=self.compress_video, args=(input_path, percentage))
        thread.start()

    def compress_video(self, input_path, percentage):
        try:
            clip = VideoFileClip(input_path)
            original_size = os.path.getsize(input_path)
            
            # Calculate target bitrate
            reduction_factor = percentage / 100
            target_bitrate = (original_size * 8 * reduction_factor) / clip.duration
            
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_{int(percentage)}pct{file_ext}"

            clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                bitrate=f"{int(target_bitrate)}",
                logger=None # Hide console logs to keep it clean
            )
            
            clip.close()
            
            new_size = os.path.getsize(output_path)
            success_msg = f"Original: {original_size / 1024 / 1024:.2f} MB\nNew: {new_size / 1024 / 1024:.2f} MB"
            
            self.after(0, lambda: self.finish_task("Success", success_msg, "green"))

        except Exception as e:
            self.after(0, lambda: self.finish_task("Error", str(e), "red"))

    def finish_task(self, title, message, color):
        self.progress_bar.stop()
        self.progress_bar.set(1)
        self.compress_btn.configure(state="normal")
        self.status_label.configure(text=title, text_color=color)
        messagebox.showinfo(title, message)

if __name__ == "__main__":
    app = VideoCompressorApp()
    app.mainloop()
