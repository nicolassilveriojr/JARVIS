import tkinter as tk
import math
import threading
import datetime
import random
import customtkinter as ctk

try:
    import psutil
    HAS_PSUTIL = True
except:
    HAS_PSUTIL = False

try:
    import numpy as np
    import pyaudio
    HAS_AUDIO = True
except:
    HAS_AUDIO = False

# ── Paleta ───────────────────────────────────────────────────
BG     = "#080c14"
PANEL  = "#0c1220"
PANEL2 = "#101828"
BORDER = "#162030"
CYAN   = "#00d4e8"
CYAN2  = "#00a8c0"
GREEN  = "#00e096"
DIM    = "#2a4a5a"
TEXT   = "#6a9ab0"
WHITE  = "#ddeeff"
RED    = "#e05555"
ACCENT = "#0e1a28"
RING1  = "#1a2a3a"
RING2  = "#142035"
RING3  = "#10182e"


class JarvisUI(ctk.CTk):
    def __init__(self, on_command=None, on_listen=None):
        super().__init__()
        self.on_command  = on_command
        self.on_listen   = on_listen
        self.on_set_api  = None
        self.listening   = False
        self.speaking    = False
        self.pulse       = 0.0
        self.rings       = []
        self.audio_level = 0.0   # 0.0 a 1.0 — nivel de audio em tempo real
        self._audio_smooth = 0.0  # versao suavizada
        self._start_time = datetime.datetime.now()

        self.title("J.A.R.V.I.S")
        self.geometry("1280x780")
        self.minsize(1050, 680)
        self.configure(fg_color=BG)
        self._build()
        self._tick()
        if HAS_AUDIO:
            threading.Thread(target=self._audio_loop, daemon=True).start()

    # ════════════════════════════════════════════════════════
    def _build(self):
        self.grid_columnconfigure(0, weight=0, minsize=300)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=370)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_left()
        self._build_center()
        self._build_right()

    # ── TOP BAR ─────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=PANEL, height=50)
        bar.grid(row=0, column=0, columnspan=3, sticky="ew")
        bar.grid_propagate(False)
        bar.columnconfigure(1, weight=1)

        logo_fr = tk.Frame(bar, bg=PANEL)
        logo_fr.grid(row=0, column=0, padx=20, pady=12, sticky="w")
        tk.Label(logo_fr, text="J.A.R.V.I.S", font=("Courier", 14, "bold"),
                 fg=WHITE, bg=PANEL).pack(side="left")
        tk.Label(logo_fr, text="  ●", font=("Courier", 9), fg=GREEN, bg=PANEL).pack(side="left", pady=2)
        tk.Label(logo_fr, text=" Online", font=("Courier", 9), fg=GREEN, bg=PANEL).pack(side="left", pady=2)

        self.top_time = tk.Label(bar, text="", font=("Courier", 11), fg=TEXT, bg=PANEL)
        self.top_time.grid(row=0, column=1)

        right_top = tk.Frame(bar, bg=PANEL)
        right_top.grid(row=0, column=2, padx=16, pady=12, sticky="e")

        self.top_clima = tk.Label(right_top, text="", font=("Courier", 10), fg=CYAN, bg=PANEL)
        self.top_clima.pack(side="left", padx=(0, 12))

        self.status_lbl = tk.Label(right_top, text="● STANDBY",
                                    font=("Courier", 10, "bold"), fg=CYAN, bg=PANEL)
        self.status_lbl.pack(side="left", padx=(0, 10))

        tk.Frame(right_top, bg=BORDER, width=1, height=22).pack(side="left", padx=6)

        self.btn_groq   = self._api_btn(right_top, "GROQ",   True,  "groq")
        self.btn_gemini = self._api_btn(right_top, "GEMINI", False, "gemini")
        self.btn_grok   = self._api_btn(right_top, "GROK",   False, "grok")

    def _api_btn(self, parent, label, active, mode):
        b = tk.Button(parent, text=label, font=("Courier", 8, "bold"),
            fg=WHITE if active else DIM,
            bg=CYAN2 if active else PANEL2,
            bd=0, padx=8, pady=3, cursor="hand2",
            command=lambda m=mode: self._set_api(m))
        b.pack(side="left", padx=2)
        return b

    # ── PAINEL ESQUERDO ──────────────────────────────────────
    def _build_left(self):
        left = tk.Frame(self, bg=PANEL, width=300)
        left.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(6, 12))
        left.grid_propagate(False)
        left.columnconfigure(0, weight=1)
        row = 0

        # System Stats
        row = self._sec(left, "⚡  System Stats", row)
        si = tk.Frame(left, bg=PANEL)
        si.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 6))
        si.columnconfigure(0, weight=1)
        row += 1

        tk.Label(si, text="CPU Usage", font=("Courier", 9), fg=TEXT, bg=PANEL).grid(row=0, column=0, sticky="w")
        self.cpu_lbl = tk.Label(si, text="0%", font=("Courier", 9), fg=CYAN, bg=PANEL)
        self.cpu_lbl.grid(row=0, column=1, sticky="e")
        bg1 = tk.Frame(si, bg=BORDER, height=4); bg1.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2,6))
        self.cpu_bar = tk.Frame(bg1, bg=CYAN, height=4); self.cpu_bar.place(x=0,y=0,relheight=1,relwidth=0.01)

        tk.Label(si, text="RAM Usage", font=("Courier", 9), fg=TEXT, bg=PANEL).grid(row=2, column=0, sticky="w")
        self.ram_lbl = tk.Label(si, text="0 GB", font=("Courier", 9), fg=CYAN, bg=PANEL)
        self.ram_lbl.grid(row=2, column=1, sticky="e")
        bg2 = tk.Frame(si, bg=BORDER, height=4); bg2.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2,8))
        self.ram_bar = tk.Frame(bg2, bg=CYAN2, height=4); self.ram_bar.place(x=0,y=0,relheight=1,relwidth=0.01)

        g3 = tk.Frame(si, bg=PANEL); g3.grid(row=4, column=0, columnspan=2, sticky="ew")
        for i, (lbl, attr) in enumerate([("CPU","mc_cpu"),("Memory","mc_mem"),("Disk","mc_dsk")]):
            g3.columnconfigure(i, weight=1)
            card = tk.Frame(g3, bg=ACCENT, padx=6, pady=6); card.grid(row=0, column=i, padx=2, sticky="ew")
            tk.Label(card, text=lbl, font=("Courier", 8), fg=DIM, bg=ACCENT).pack()
            v = tk.Label(card, text="—", font=("Courier", 9, "bold"), fg=WHITE, bg=ACCENT); v.pack()
            setattr(self, attr, v)

        row = self._div(left, row)

        # Weather
        row = self._sec(left, "☁  Weather", row)
        wx = tk.Frame(left, bg=PANEL); wx.grid(row=row, column=0, sticky="ew", padx=14, pady=(0,8))
        wx.columnconfigure(0, weight=1); row += 1
        self.wx_temp = tk.Label(wx, text="—", font=("Courier", 26, "bold"), fg=WHITE, bg=PANEL); self.wx_temp.grid(row=0, column=0, sticky="w")
        self.wx_city = tk.Label(wx, text="Carregando...", font=("Courier", 9), fg=TEXT, bg=PANEL); self.wx_city.grid(row=1, column=0, sticky="w")
        self.wx_desc = tk.Label(wx, text="", font=("Courier", 9), fg=DIM, bg=PANEL); self.wx_desc.grid(row=2, column=0, sticky="w")
        wg = tk.Frame(wx, bg=PANEL); wg.grid(row=3, column=0, sticky="ew", pady=(8,0))
        for i, (lbl, attr) in enumerate([("Humidity","wx_hum"),("Wind","wx_wind"),("Feels Like","wx_feel")]):
            wg.columnconfigure(i, weight=1)
            card = tk.Frame(wg, bg=ACCENT, padx=4, pady=4); card.grid(row=0, column=i, padx=2, sticky="ew")
            tk.Label(card, text=lbl, font=("Courier", 7), fg=DIM, bg=ACCENT).pack()
            v = tk.Label(card, text="—", font=("Courier", 8, "bold"), fg=WHITE, bg=ACCENT); v.pack()
            setattr(self, attr, v)

        row = self._div(left, row)

        # Camera
        row = self._sec(left, "📷  Camera", row)
        cam = tk.Frame(left, bg="#060a10", height=100)
        cam.grid(row=row, column=0, sticky="ew", padx=14, pady=(0,4)); cam.grid_propagate(False)
        self.cam_label = tk.Label(cam, text="Camera inactive", font=("Courier", 9), fg=DIM, bg="#060a10")
        self.cam_label.place(relx=0.5, rely=0.5, anchor="center")
        row += 1
        tk.Label(left, text="Camera active. Click the camera icon to take a snapshot.",
                 font=("Courier", 8), fg=DIM, bg=PANEL, wraplength=260).grid(row=row, column=0, padx=14, sticky="w")
        row += 1

        row = self._div(left, row)

        # Uptime
        up = tk.Frame(left, bg=PANEL); up.grid(row=row, column=0, sticky="ew", padx=14, pady=(4,12))
        up.columnconfigure(0, weight=1)
        tk.Label(up, text="ℹ  System Uptime", font=("Courier", 9), fg=DIM, bg=PANEL).grid(row=0, column=0, sticky="w")
        self.uptime_lbl = tk.Label(up, text="00:00:00", font=("Courier", 9), fg=TEXT, bg=PANEL)
        self.uptime_lbl.grid(row=0, column=1, sticky="e")

        threading.Thread(target=self._load_weather, daemon=True).start()

    # ── CENTRO ───────────────────────────────────────────────
    def _build_center(self):
        c = tk.Frame(self, bg=BG)
        c.grid(row=1, column=1, sticky="nsew", pady=(6,12))
        c.rowconfigure(0, weight=1)
        c.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(c, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        tk.Label(c, text="J.A.R.V.I.S", font=("Courier", 17, "bold"),
                 fg=WHITE, bg=BG).grid(row=1, column=0, pady=(10,4))

        self.center_status = tk.Label(c, text="● Sistema Online",
                                       font=("Courier", 10), fg=GREEN, bg=BG)
        self.center_status.grid(row=2, column=0, pady=(0,14))

        btns = tk.Frame(c, bg=BG); btns.grid(row=3, column=0, pady=(0,18))
        self._cbtn(btns, "👁",  self._cmd_cam).pack(side="left", padx=10)
        self._cbtn(btns, "🎤", self._ouvir).pack(side="left", padx=10)
        self._cbtn(btns, "⌨",  self._focus_entry).pack(side="left", padx=10)

    # ── PAINEL DIREITO ────────────────────────────────────────
    def _build_right(self):
        r = tk.Frame(self, bg=PANEL, width=370)
        r.grid(row=1, column=2, sticky="nsew", padx=(6,12), pady=(6,12))
        r.grid_propagate(False)
        r.rowconfigure(1, weight=1)
        r.columnconfigure(0, weight=1)

        hdr = tk.Frame(r, bg=PANEL); hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(14,8))
        hdr.columnconfigure(0, weight=1)
        tk.Label(hdr, text="Conversation", font=("Courier", 13, "bold"), fg=WHITE, bg=PANEL).grid(row=0, column=0, sticky="w")

        lf = tk.Frame(r, bg=PANEL); lf.grid(row=1, column=0, sticky="nsew", padx=10)
        lf.rowconfigure(0, weight=1); lf.columnconfigure(0, weight=1)
        self.log_text = tk.Text(lf, bg=PANEL, fg=TEXT, font=("Courier", 10),
            bd=0, wrap="word", state="disabled", selectbackground=CYAN2,
            insertbackground=CYAN, spacing1=3, spacing3=3)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        sb = tk.Scrollbar(lf, command=self.log_text.yview, bg=PANEL2, troughcolor=BG, width=5)
        sb.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.tag_config("jarvis", foreground=CYAN)
        self.log_text.tag_config("user",   foreground=WHITE)
        self.log_text.tag_config("sys",    foreground=DIM)
        self.log_text.tag_config("err",    foreground=RED)
        self.log_text.tag_config("ts",     foreground=DIM)

        tk.Frame(r, bg=BORDER, height=1).grid(row=2, column=0, sticky="ew", padx=10, pady=4)

        ef = tk.Frame(r, bg=PANEL2); ef.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,12))
        ef.columnconfigure(0, weight=1)
        self.entry = tk.Entry(ef, font=("Courier", 11), bg=PANEL2, fg=DIM,
            insertbackground=CYAN, bd=0, relief="flat")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(12,4), pady=10)
        self.entry.insert(0, "Type a message...")
        self.entry.bind("<FocusIn>",  self._ein)
        self.entry.bind("<FocusOut>", self._eout)
        self.entry.bind("<Return>",   self._on_enter)
        tk.Button(ef, text="➤", font=("Courier", 12), fg=BG, bg=CYAN, bd=0,
            padx=10, pady=6, activebackground=CYAN2, cursor="hand2",
            command=self._enviar).grid(row=0, column=1, padx=(0,6))

    # ════════════════════════════════════════════════════════
    #  HELPERS
    # ════════════════════════════════════════════════════════
    def _sec(self, p, t, row):
        f = tk.Frame(p, bg=PANEL); f.grid(row=row, column=0, sticky="ew", padx=14, pady=(10,4))
        tk.Label(f, text=t, font=("Courier", 9, "bold"), fg=TEXT, bg=PANEL).pack(side="left")
        return row + 1

    def _div(self, p, row):
        tk.Frame(p, bg=BORDER, height=1).grid(row=row, column=0, sticky="ew", padx=12, pady=4)
        return row + 1

    def _cbtn(self, p, t, cmd):
        return tk.Button(p, text=t, font=("Arial", 14), fg=WHITE, bg=ACCENT,
            bd=0, padx=18, pady=14, activebackground=RING1, cursor="hand2",
            relief="flat", command=cmd)

    def _ein(self, e):
        if self.entry.get() == "Type a message...":
            self.entry.delete(0, "end"); self.entry.configure(fg=WHITE)

    def _eout(self, e):
        if not self.entry.get():
            self.entry.insert(0, "Type a message..."); self.entry.configure(fg=DIM)

    def _cmd_cam(self):
        if self.on_command:
            threading.Thread(target=self.on_command, args=("webcam",), daemon=True).start()

    def _focus_entry(self):
        self.entry.focus_set()

    def _load_weather(self):
        try:
            import urllib.request, json
            with urllib.request.urlopen("https://wttr.in/?format=j1", timeout=6) as r:
                d = json.loads(r.read())
            cur  = d["current_condition"][0]
            temp = cur["temp_C"]; desc = cur["weatherDesc"][0]["value"]
            hum  = cur["humidity"] + "%"; wind = cur["windspeedKmph"] + " km/h"
            feel = cur["FeelsLikeC"] + "°C"
            city = d.get("nearest_area",[{}])[0].get("areaName",[{}])[0].get("value","")
            self.wx_temp.configure(text=f"{temp}°C")
            self.wx_city.configure(text=city)
            self.wx_desc.configure(text=desc)
            self.wx_hum.configure(text=hum)
            self.wx_wind.configure(text=wind)
            self.wx_feel.configure(text=feel)
            self.top_clima.configure(text=f"{temp}°C  {city}")
        except:
            self.wx_temp.configure(text="—"); self.wx_city.configure(text="Sem conexão")

    # ════════════════════════════════════════════════════════
    #  API PÚBLICA
    # ════════════════════════════════════════════════════════
    def log(self, who, msg, tag="sys"):
        self.log_text.configure(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M")
        if tag == "user":
            self.log_text.insert("end", f"\n  {msg}\n", "user")
        else:
            t = "jarvis" if who == "JARVIS" else tag
            self.log_text.insert("end", f"\n• {msg}\n", t)
        self.log_text.insert("end", f"  {ts}\n", "ts")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def set_status(self, text, color=CYAN):
        self.status_lbl.configure(text=text, fg=color)
        clean = text.lstrip("●◈◎ ")
        self.center_status.configure(text=f"● {clean}", fg=color)

    def _on_enter(self, e=None): self._enviar()

    def _enviar(self):
        txt = self.entry.get().strip()
        if not txt or txt == "Type a message...": return
        self.entry.delete(0, "end")
        self.log("VOCÊ", txt, "user")
        if self.on_command:
            threading.Thread(target=self.on_command, args=(txt,), daemon=True).start()

    def _ouvir(self):
        if self.on_listen:
            threading.Thread(target=self.on_listen, daemon=True).start()

    def _set_api(self, modo):
        for btn, m in [(self.btn_groq,"groq"),(self.btn_gemini,"gemini"),(self.btn_grok,"grok")]:
            a = (m == modo)
            btn.configure(bg=CYAN2 if a else PANEL2, fg=WHITE if a else DIM)
        if self.on_set_api: self.on_set_api(modo)

    # ════════════════════════════════════════════════════════
    #  AUDIO REATIVO
    # ════════════════════════════════════════════════════════
    def _audio_loop(self):
        """Captura nivel de audio do microfone em tempo real"""
        try:
            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=512
            )
            while True:
                try:
                    data = stream.read(512, exception_on_overflow=False)
                    arr  = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                    rms  = float(np.sqrt(np.mean(arr ** 2)))
                    # Normaliza para 0.0-1.0 (voz normal ~500-3000 RMS)
                    level = min(1.0, rms / 2500.0)
                    self.audio_level = level
                except:
                    self.audio_level = 0.0
        except:
            HAS_AUDIO = False

    # ════════════════════════════════════════════════════════
    #  TICK + DESENHO
    # ════════════════════════════════════════════════════════
    def _tick(self):
        self.pulse    += 0.035
        self._frame    = getattr(self, "_frame", 0) + 1
        self._ring_cd  = getattr(self, "_ring_cd", 0) - 1

        # Suaviza o nivel de audio (lerp) para animacao fluida
        target_audio = self.audio_level if (self.listening or self.speaking) else 0.0
        self._audio_smooth += (target_audio - self._audio_smooth) * 0.25
        now = datetime.datetime.now()

        # Hora
        self.top_time.configure(text=now.strftime("%H:%M:%S   |   %d/%m/%Y"))

        # Uptime
        delta = now - self._start_time
        h, rem = divmod(int(delta.total_seconds()), 3600)
        m, s   = divmod(rem, 60)
        self.uptime_lbl.configure(text=f"{h:02d}:{m:02d}:{s:02d}")

        # Stats a cada ~1.5s em thread separada para nao travar
        if self._frame % 50 == 0 and HAS_PSUTIL:
            threading.Thread(target=self._update_stats, daemon=True).start()

        # Spawn anel com cooldown fixo (sem modulo de float)
        if self._ring_cd <= 0:
            spd = random.uniform(0.8, 1.4) if (self.listening or self.speaking) \
                  else random.uniform(0.35, 0.6)
            self.rings.append({"r": 0.0, "speed": spd, "alpha": 1.0})
            self._ring_cd = 18 if (self.listening or self.speaking) else 45

        # Atualiza aneis
        novos = []
        for rg in self.rings:
            rg["r"]     += rg["speed"] * 2.0
            rg["alpha"] -= 0.012
            if rg["alpha"] > 0:
                novos.append(rg)
        self.rings = novos

        self._draw()
        self.after(40, self._tick)

    def _update_stats(self):
        try:
            cpu  = psutil.cpu_percent(interval=0.4)
            ram  = psutil.virtual_memory()
            disk = psutil.disk_usage("C:/")
            self.after(0, lambda: self._apply_stats(cpu, ram, disk))
        except:
            pass

    def _apply_stats(self, cpu, ram, disk):
        try:
            self.cpu_lbl.configure(text=f"{cpu:.0f}%")
            self.ram_lbl.configure(text=f"{ram.used/1024**3:.1f} GB")
            self.cpu_bar.place(relwidth=max(0.02, cpu/100))
            self.ram_bar.place(relwidth=max(0.02, ram.percent/100))
            self.mc_cpu.configure(text=f"{cpu:.0f}%")
            self.mc_mem.configure(text=f"{ram.percent:.0f}%")
            used_g = disk.used  // (1024**3)
            tot_g  = disk.total // (1024**3)
            self.mc_dsk.configure(text=f"{used_g}/{tot_g}GB")
        except:
            pass

    def _draw(self):
        cv = self.canvas
        cv.delete("all")
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 20 or h < 20:
            return
        cx, cy = w // 2, h // 2
        R = min(w, h) // 2 - 24

        # ── Círculos concêntricos estáticos — 4 ovais fixas ──
        cv.create_oval(cx-R,          cy-R,          cx+R,          cy+R,          fill="#0b1220", outline=RING1, width=1)
        cv.create_oval(cx-R*3//4,     cy-R*3//4,     cx+R*3//4,     cy+R*3//4,     fill="#0d1528", outline=RING1, width=1)
        cv.create_oval(cx-R//2,       cy-R//2,       cx+R//2,       cy+R//2,       fill="#101830", outline=RING2, width=1)
        cv.create_oval(cx-R*7//25,    cy-R*7//25,    cx+R*7//25,    cy+R*7//25,    fill="#0f1a35", outline=RING3, width=2)

        # ── Anéis sonar — máximo 4 simultâneos ──
        for ring in self.rings[-4:]:
            r = int(ring["r"])
            if r >= R:
                continue
            a   = ring["alpha"]
            val = int(a * 140)
            col = f"#00{min(255, val//3):02x}{min(255, val+50):02x}"
            cv.create_oval(cx-r, cy-r, cx+r, cy+r, outline=col, width=max(1, int(a*2)))

        # ── Núcleo reativo ao áudio ──
        al = self._audio_smooth

        p1 = int(44 + al * 52 + 4 * math.sin(self.pulse))
        p2 = int(30 + al * 32 + 3 * math.sin(self.pulse + 1.2))
        p3 = int(17 + al * 18 + 2 * math.sin(self.pulse + 2.4))

        # Glow — apenas 3 camadas fixas (sem loop pesado)
        g = int(al * 70)
        cv.create_oval(cx-p1-14, cy-p1-14, cx+p1+14, cy+p1+14, outline=f"#00{g//4:02x}{min(255,g+20):02x}", width=1)
        cv.create_oval(cx-p1-7,  cy-p1-7,  cx+p1+7,  cy+p1+7,  outline=f"#00{g//2:02x}{min(255,g+50):02x}", width=1)
        cv.create_oval(cx-p1-2,  cy-p1-2,  cx+p1+2,  cy+p1+2,  outline=f"#00{g:02x}{min(255,g+80):02x}",    width=1)

        # Cor do anel externo varia com audio
        iv = int(al * 200)
        oc = f"#00{min(255,90+iv//2):02x}{min(255,170+iv//4):02x}"

        cv.create_oval(cx-p1, cy-p1, cx+p1, cy+p1, fill="#0d1e32", outline=oc,   width=2)
        cv.create_oval(cx-p2, cy-p2, cx+p2, cy+p2, fill="#0f2540", outline=CYAN2, width=2)
        cv.create_oval(cx-p3, cy-p3, cx+p3, cy+p3, fill="#1a3a5a", outline=CYAN,  width=1)

        # Pontinhos centrais
        active = self.listening or self.speaking
        dot    = CYAN if active else "#2a5a7a"
        bi     = int(self.pulse * (3 + al * 5)) % 5
        rd     = int(3 + al * 3)
        for i, dx in enumerate([-14, -7, 0, 7, 14]):
            col = CYAN if (active and i == bi) else dot
            cv.create_oval(cx+dx-rd, cy-rd, cx+dx+rd, cy+rd, fill=col, outline="")