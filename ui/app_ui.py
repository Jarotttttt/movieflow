# d:\Tools\Movie Flow\ui\app_ui.py
import customtkinter as ctk
import tksvg
from datetime import datetime

ctk.set_appearance_mode("dark")

# ── Tema Warna Baru (Neon Cyan / Dark Mode Premium) ──
BG            = "#09090B"  # Zinc 950 (Background utama)
CARD_BG       = "#18181B"  # Zinc 900 (Background kartu)
CARD_HOVER    = "#27272A"  # Zinc 800
BORDER_COLOR  = "#3F3F46"  # Zinc 700
TEXT_MAIN     = "#FAFAFA"  # Zinc 50
TEXT_MUTED    = "#A1A1AA"  # Zinc 400
ACCENT_CYAN   = "#06B6D4"  # Cyan 500
ACCENT_HOVER  = "#0891B2"  # Cyan 600
GREEN_COLOR   = "#10B981"  # Emerald 500
RED_COLOR     = "#EF4444"  # Red 500

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AppUI:
    def __init__(self, window, app_name, app_version, on_start, on_stop):
        self.window = window
        self.window.title(f"{app_name} {app_version}")
        self.window.geometry("1100x750")
        self.window.minsize(900, 600)
        self.window.configure(fg_color=BG)
        
        # Set taskbar/window icon
        try:
            self.window.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass

        self.status_text = ctk.StringVar(value="MENUNGGU INSTRUKSI")
        self._build(app_name, app_version, on_start, on_stop)
        self._tick()
        self.log("Sistem diinisialisasi dan siap beroperasi.")

    def _tick(self):
        self.clock.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.window.after(1000, self._tick)

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] ", "time")
        self.log_box.insert("end", f"{msg}\n", "msg")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _build(self, app_name, app_version, on_start, on_stop):
        # ── Layout Utama: 1 Kolom, 4 Baris (Dashboard Style) ──
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(3, weight=1)  # Area log mengambil sisa ruang bawah

        # ── 1. HEADER ──
        header = ctk.CTkFrame(self.window, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        header.grid_columnconfigure(1, weight=1)

        # Load SVG Icons
        self.logo_img = tksvg.SvgImage(file=resource_path(os.path.join("assets", "logo.svg")), scale=1.2)
        ctk.CTkLabel(header, text="", image=self.logo_img).grid(row=0, column=0, padx=(0, 12))
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(title_box, text=app_name.upper(), font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(title_box, text=f"  {app_version}", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(side="left", pady=(4, 0))

        self.clock = ctk.CTkLabel(header, text="", font=ctk.CTkFont(family="Consolas", size=16, weight="bold"), text_color=ACCENT_CYAN)
        self.clock.grid(row=0, column=2, sticky="e")

        # ── 2. STATISTIK (DASHBOARD CARDS HORIZONTAL) ──
        stats_container = ctk.CTkFrame(self.window, fg_color="transparent")
        stats_container.grid(row=1, column=0, sticky="ew", padx=26, pady=(0, 20))
        stats_container.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_target = self._build_stat_card(stats_container, 0, "TARGET AKUN", "0", TEXT_MAIN)
        self.stat_ok = self._build_stat_card(stats_container, 1, "BERHASIL DIBUAT", "0", GREEN_COLOR)
        self.stat_fail = self._build_stat_card(stats_container, 2, "GAGAL PROSES", "0", RED_COLOR)

        # ── 3. ACTION BAR (KONTROL ALAT) ──
        action_bar = ctk.CTkFrame(self.window, fg_color=CARD_BG, corner_radius=12, border_color=BORDER_COLOR, border_width=1)
        action_bar.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 20))
        action_bar.grid_columnconfigure(5, weight=1) # Spacer tengah untuk dorong status ke kanan

        # Input Jumlah
        ctk.CTkLabel(action_bar, text="JUMLAH:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=0, padx=(24, 10), pady=24)
        self.count_var = ctk.StringVar(value="3")
        ctk.CTkEntry(action_bar, textvariable=self.count_var, fg_color=BG, border_color=BORDER_COLOR, text_color=TEXT_MAIN, corner_radius=6, width=80, height=38, font=ctk.CTkFont(size=15, weight="bold"), justify="center").grid(row=0, column=1, padx=(0, 24))

        # Separator vertikal
        ctk.CTkFrame(action_bar, width=1, height=30, fg_color=BORDER_COLOR).grid(row=0, column=2, padx=(0, 24))

        # Load SVG Icons for buttons
        self.play_img = tksvg.SvgImage(file=resource_path(os.path.join("assets", "play.svg")), scale=0.8)
        self.stop_img = tksvg.SvgImage(file=resource_path(os.path.join("assets", "stop.svg")), scale=0.8)

        # Tombol Aksi
        self.start_btn = ctk.CTkButton(action_bar, text=" MULAI PROSES", image=self.play_img, command=on_start, fg_color=ACCENT_CYAN, hover_color=ACCENT_HOVER, text_color="#000000", height=38, corner_radius=6, font=ctk.CTkFont(size=13, weight="bold"))
        self.start_btn.grid(row=0, column=3, padx=(0, 12))

        self.stop_btn = ctk.CTkButton(action_bar, text=" BERHENTI", image=self.stop_img, command=on_stop, fg_color="transparent", hover_color=CARD_HOVER, border_color=RED_COLOR, border_width=1, text_color=RED_COLOR, height=38, corner_radius=6, font=ctk.CTkFont(size=13, weight="bold"), state="disabled")
        self.stop_btn.grid(row=0, column=4, padx=(0, 24))

        # Indikator Status (Kanan)
        status_frame = ctk.CTkFrame(action_bar, fg_color="transparent")
        status_frame.grid(row=0, column=6, sticky="e", padx=24)
        ctk.CTkLabel(status_frame, text="STATUS:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(side="left", padx=(0, 12))
        self.status_badge = ctk.CTkLabel(status_frame, textvariable=self.status_text, font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MAIN, fg_color=BG, corner_radius=6, width=160, height=34)
        self.status_badge.pack(side="left")

        # ── 4. LOG AKTIVITAS ──
        log_container = ctk.CTkFrame(self.window, fg_color=CARD_BG, corner_radius=12, border_color=BORDER_COLOR, border_width=1)
        log_container.grid(row=3, column=0, sticky="nsew", padx=30, pady=(0, 30))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_container, fg_color="transparent", height=40)
        log_header.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 0))
        ctk.CTkLabel(log_header, text="LOG TERMINAL", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        self.log_box = ctk.CTkTextbox(log_container, fg_color=BG, text_color=TEXT_MAIN, font=ctk.CTkFont(family="Consolas", size=13), wrap="word", corner_radius=8, border_color=BORDER_COLOR, border_width=1)
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(12, 20))

        # Pengaturan warna teks di log
        self.log_box.tag_config("time", foreground=ACCENT_CYAN)
        self.log_box.tag_config("msg", foreground=TEXT_MAIN)

    def _build_stat_card(self, parent, col, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12, border_color=BORDER_COLOR, border_width=1)
        card.grid(row=0, column=col, sticky="nsew", padx=4)
        card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(pady=(24, 6))
        lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=42, weight="bold"), text_color=color)
        lbl.pack(pady=(0, 24))
        return lbl

