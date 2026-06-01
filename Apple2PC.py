# Fix for PyInstaller EXE packaging
import sys
import multiprocessing
if getattr(sys, 'frozen', False):
    multiprocessing.freeze_support()

import os
if getattr(sys, 'frozen', False) and sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

import os
import tkinter as tk
from tkinter import filedialog, ttk
import qrcode
from PIL import ImageTk, Image
import subprocess
import socket
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
from typing import Optional, List
import atexit
import threading

# ===================== CONFIG =====================
PORT = 8266
RULE_NAME = "PhoneTransfer_Auto"
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

save_folder = os.path.join(os.path.expanduser("~"), "PhoneUploads")
os.makedirs(save_folder, exist_ok=True)
app_ui = None

# ===================== FIREWALL =====================
def add_firewall():
    try:
        subprocess.run(
            f'netsh advfirewall firewall add rule name={RULE_NAME} dir=in action=allow protocol=TCP localport={PORT} profile=any enable=yes',
            shell=True, capture_output=True
        )
    except:
        pass

def remove_firewall():
    try:
        subprocess.run(
            f'netsh advfirewall firewall delete rule name={RULE_NAME}',
            shell=True, capture_output=True
        )
    except:
        pass

atexit.register(remove_firewall)

# ===================== GET IP =====================
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 8))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ===================== SELECT FOLDER =====================
def select_folder():
    global save_folder
    folder = filedialog.askdirectory(title="Select Save Folder", initialdir=save_folder)
    if folder:
        save_folder = folder
        os.makedirs(save_folder, exist_ok=True)
        app_ui.path_label.config(text=f"Save Path: {save_folder}")

def open_save_folder():
    try:
        os.startfile(save_folder)
    except:
        pass

# ===================== HOME PAGE =====================
@app.get("/")
async def index():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Transfer</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f7f8fa;padding:40px 20px;text-align:center}
        .title{font-size:32px;font-weight:bold;color:#2c3e50;margin-bottom:10px}
        .tip{font-size:18px;color:#7f8c8d;margin-bottom:30px}
        .card{background:white;padding:40px 25;border-radius:24px;box-shadow:0 8px 30px rgba(0,0,0,0.08)}
        .btn{display:block;width:100%;font-size:26px;font-weight:bold;padding:22px 0;border-radius:16px;margin-bottom:18px;cursor:pointer;border:none;background:#007bff;color:white}
        #file_input{display:none}
        #file_name{font-size:18px;color:#555;margin-bottom:20px}
    </style>
</head>
<body>
    <div class="title">📤 Wireless File Transfer</div>
    <div class="tip">Select files and upload to PC</div>
    <div class="card">
        <input type="file" multiple id="file_input" name="files">
        <label class="btn" for="file_input">1 - Choose Files</label>
        <div id="file_name">No files selected</div>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" multiple name="files" style="display:none" id="real_file">
            <button class="btn" type="submit">2 - Upload Files</button>
        </form>
    </div>
    <script>
        const real = document.getElementById('real_file');
        const fake = document.getElementById('file_input');
        const nameLabel = document.getElementById('file_name');

        fake.addEventListener('change', () => {
            real.files = fake.files;
            if (fake.files.length > 0) {
                nameLabel.textContent = "Selected: " + Array.from(fake.files).map(f => f.name).join(", ");
            } else {
                nameLabel.textContent = "No files selected";
            }
        });
    </script>
</body>
</html>
""")

# ===================== UPLOAD API =====================
@app.post("/upload")
async def upload_files(files: Optional[List[UploadFile]] = File(None)):
    if not files:
        return HTMLResponse("""
<div style='background:#fff3cd;color:#856404;padding:40px;border-radius:24px;font-size:28px;text-align:center'>
⚠️ Please select files first
</div>""")
    try:
        for f in files:
            dst = os.path.join(save_folder, f.filename)
            with open(dst, "wb") as o:
                shutil.copyfileobj(f.file, o)
        return HTMLResponse("""
<div style='background:#d4edda;color:#155724;padding:50px;border-radius:24px;font-size:32px;font-weight:bold;text-align:center'>
✅ Upload Successful!<br>Check your PC folder!
</div>""")
    except Exception as e:
        return HTMLResponse("""
<div style='background:#f8d7da;color:#721c20;padding:40px;border-radius:24px;font-size:28px;text-align:center'>
❌ Upload Failed
</div>""")

# ===================== START SERVER =====================
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="critical")

# ===================== NEW PROFESSIONAL UI =====================
class FileTransferGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wireless File Transfer")
        self.geometry("560x680")
        self.resizable(False, False)
        self.configure(bg="#ffffff")
        self.qr_img = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # ========== Top Bar (Title Centered) ==========
        top_frame = tk.Frame(self, bg="#165DFF", height=50)
        top_frame.pack(fill="x", side="top")
        top_frame.pack_propagate(False)

        title_label = tk.Label(top_frame, text="Wireless Transfer", font=("Segoe UI", 16, "bold"), bg="#165DFF", fg="white")
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        self.status_label = tk.Label(top_frame, text="🔴 Stopped", font=("Segoe UI", 11), bg="#165DFF", fg="white")
        self.status_label.pack(side="right", padx=16)

        # ========== QR Code Area ==========
        qr_container = tk.Frame(self, bg="white", padx=30, pady=20)
        qr_container.pack(pady=10)

        self.qr_label = tk.Label(qr_container, bg="#F5F7FA", relief="flat", width=280, height=280)
        self.qr_label.pack()

        self.ip_label = tk.Label(self, text="Initializing...", font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50")
        self.ip_label.pack(pady=6)

        # ========== Action Buttons (More Beautiful) ==========
        btn_frame = tk.Frame(self, bg="white", pady=10)
        btn_frame.pack()

        style = ttk.Style()
        style.configure("Action.TButton", font=("Segoe UI", 11), padding=12)

        select_btn = ttk.Button(btn_frame, text="📁 Select Folder", style="Action.TButton", command=select_folder, width=16)
        select_btn.grid(row=0, column=0, padx=12)

        open_btn = ttk.Button(btn_frame, text="📂 Open Folder", style="Action.TButton", command=open_save_folder, width=16)
        open_btn.grid(row=0, column=1, padx=12)

        # ========== Important Tips (Clear & Beautiful) ==========
        tk.Label(self, text="⚠️ Phone & PC must be on the SAME Wi-Fi",
                 font=("Segoe UI", 11, "bold"), bg="white", fg="#d93025").pack(pady=6)
        tk.Label(self, text="Scan QR code with camera or browser to transfer files",
                 font=("Segoe UI", 10), bg="white", fg="#666666").pack()

        # ========== Save Path ==========
        self.path_label = tk.Label(self, text=f"Save Path: {save_folder}",
                                   font=("Segoe UI", 10), bg="white", fg="#444444", wraplength=500)
        self.path_label.pack(pady=16)

        # ========== Start Service ==========
        self.after(300, self.start_service)

    def start_service(self):
        add_firewall()
        ip = get_ip()
        url = f"http://{ip}:{PORT}"
        self.ip_label.config(text=f"Access: {url}")
        self.status_label.config(text="🟢 Running")
        self.generate_qr(url)
        threading.Thread(target=run_server, daemon=True).start()

    def generate_qr(self, url):
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").resize((260, 260))
        self.qr_img = ImageTk.PhotoImage(img)
        self.qr_label.config(image=self.qr_img)

    def on_close(self):
        remove_firewall()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app_ui = FileTransferGUI()
    app_ui.mainloop()