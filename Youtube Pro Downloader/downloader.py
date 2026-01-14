import customtkinter as ctk
from tkinter import messagebox
import yt_dlp
import threading
import re
import os
import sys

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "ffmpeg.exe")

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class AppDescargador(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Pro Downloader v2.0")
        self.geometry("650x500")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#1e1e1e", border_width=2, border_color="#333333")
        self.main_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.label_titulo = ctk.CTkLabel(self.main_frame, text="YOUTUBE PRO", font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="#E0E0E0")
        self.label_titulo.pack(pady=(40, 5))

        self.label_sub = ctk.CTkLabel(self.main_frame, text="High Quality Media Downloader", font=ctk.CTkFont(size=14), text_color="#888888")
        self.label_sub.pack(pady=(0, 30))

        self.entrada_url = ctk.CTkEntry(self.main_frame, placeholder_text="Paste YouTube URL here...", width=500, height=45, corner_radius=10, border_color="#444444", fg_color="#2b2b2b")
        self.entrada_url.pack(pady=10)

        self.opcion_formato = ctk.CTkSegmentedButton(self.main_frame, values=["Video (MP4)", "Audio (MP3)"], font=ctk.CTkFont(size=13, weight="bold"), selected_color="#cc0000", selected_hover_color="#ff0000", height=35)
        self.opcion_formato.set("Video (MP4)")
        self.opcion_formato.pack(pady=20)

        self.btn_descargar = ctk.CTkButton(self.main_frame, text="START DOWNLOAD", command=self.start_thread, font=ctk.CTkFont(size=16, weight="bold"), height=50, width=250, corner_radius=25, fg_color="#cc0000", hover_color="#ff0000")
        self.btn_descargar.pack(pady=25)

        self.label_estado = ctk.CTkLabel(self.main_frame, text="Ready to start", font=ctk.CTkFont(size=13), text_color="#AAAAAA")
        self.label_estado.pack(pady=(5, 5))
        
        self.progreso = ctk.CTkProgressBar(self.main_frame, width=450, height=12, corner_radius=10, progress_color="#cc0000", fg_color="#333333")
        self.progreso.set(0)
        self.progreso.pack(pady=(5, 40))

    def clean_text(self, text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p_raw = d.get('_percent_str', '0%')
            p_clean = self.clean_text(p_raw).replace('%','').strip()
            try:
                val = float(p_clean) / 100
                self.progreso.set(val)
                self.label_estado.configure(text=f"Downloading: {p_clean}%")
            except:
                pass
            self.update_idletasks()

    def start_thread(self):
        thread = threading.Thread(target=self.execute_download, daemon=True)
        thread.start()

    def execute_download(self):
        url = self.entrada_url.get()
        fmt = self.opcion_formato.get()

        if not url:
            messagebox.showwarning("Warning", "Please paste a URL first")
            return

        self.btn_descargar.configure(state="disabled")
        self.label_estado.configure(text="Connecting to YouTube...")
        
        try:
            ydl_opts = {
                'progress_hooks': [self.progress_hook],
                'outtmpl': '%(title)s.%(ext)s',
                'nocolors': True,
                'quiet': True,
                'no_warnings': True,
                'ffmpeg_location': get_ffmpeg_path()
            }
            
            if fmt == "Video (MP4)":
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                })
            else:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if fmt == "Audio (MP3)":
                    filename = os.path.splitext(filename)[0] + ".mp3"
                
                full_path = os.path.abspath(filename)

            self.label_estado.configure(text="Download Completed")
            messagebox.showinfo("Success", f"File saved at:\n\n{full_path}")
            self.progreso.set(0)
            
        except Exception:
            messagebox.showerror("Error", "Invalid URL or connection failed.")
            self.label_estado.configure(text="Error")
        
        self.btn_descargar.configure(state="normal")

if __name__ == "__main__":
    app = AppDescargador()
    app.mainloop()