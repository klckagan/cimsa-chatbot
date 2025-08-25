from pathlib import Path
from PIL import Image, ImageFilter
import customtkinter as ctk
import tkinter.filedialog as fd
from chatbot_logic import get_bot_response
import time

APP_TITLE = "Çimsa Akıllı Asistan"
LOGO_FILE = Path("logo.png")
BACKGROUND_FILE = Path("cimsa_bg.png")
ATTACH_DIR = Path("attachments")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  

SABANCI_NAVY = "#001E62"
SABANCI_NAVY_HOVER = "#0A2E8A"
WELCOME_LIGHT = "#DFF3E2"
WELCOME_DARK  = "#1E2E24"

COLORS = {
    "card":      ( "#FFFFFF", "#151A21"),
    "user_bg":   ( "#E9EEFF", "#0B1F3D"),   
    "user_fg":   ( "#001E62", "#D6E2FF"),   
    "bot_bg":    ( "#F2F6FF", "#2E3B4E"),   
    "bot_fg":    ( "#001E62", "#FFFFFF"),   
    "chip_bg":   ( "#EEF3FF", "#162238"),
    "btn_fg":    SABANCI_NAVY,
    "btn_hover": SABANCI_NAVY_HOVER,
    "welcome_bg": (WELCOME_LIGHT, WELCOME_DARK),
    "welcome_fg": ( "#103820", "#CFEDD6"),
    "section":   ( "#E8EEF9", "#0E1A32"),
}

WRAP = 760

def exists(p: Path) -> bool:
    try: return p.exists()
    except: return False


class ChatArea(ctk.CTkScrollableFrame):
    """2 kolon: sol=kullanıcı, sağ=bot. 'system' için ortalı yeşil bar."""
    def __init__(self, master, font_body, font_small):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.font_body = font_body
        self.font_small = font_small
        self.grid_columnconfigure(0, weight=1)

    def _row_container(self):
        row = self.grid_size()[1]
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.grid(row=row, column=0, sticky="ew", pady=(6, 6))
        cont.grid_columnconfigure(0, weight=1)  
        cont.grid_columnconfigure(1, weight=1)  
        return cont

    def add_user(self, text: str):
        cont = self._row_container()
        lbl = ctk.CTkLabel(
            cont, text=text, wraplength=WRAP, justify="left",
            fg_color=COLORS["user_bg"], text_color=COLORS["user_fg"],
            corner_radius=12, padx=14, pady=10, font=self.font_body
        )
        lbl.grid(row=0, column=0, sticky="w", padx=(12, 40))
        self.after(30, lambda: self._parent_canvas.yview_moveto(1.0))

    def add_bot(self, text: str):
        cont = self._row_container()
        lbl = ctk.CTkLabel(
            cont, text=text, wraplength=WRAP, justify="left",
            fg_color=COLORS["bot_bg"], text_color=COLORS["bot_fg"],
            corner_radius=12, padx=14, pady=10, font=self.font_body
        )
        lbl.grid(row=0, column=1, sticky="e", padx=(40, 12))
        self.after(30, lambda: self._parent_canvas.yview_moveto(1.0))

    def add_system_welcome(self, text: str):
        row = self.grid_size()[1]
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.grid(row=row, column=0, sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(box, fg_color=COLORS["welcome_bg"], corner_radius=14)
        inner.grid(row=0, column=0, padx=12, pady=(8, 2))
        ctk.CTkLabel(
            inner, text=text, font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["welcome_fg"], justify="center", wraplength=900
        ).pack(padx=16, pady=10)
        self.after(30, lambda: self._parent_canvas.yview_moveto(1.0))

    def add_suggestions(self, items, on_click):
        cont = self._row_container()
        box = ctk.CTkFrame(cont, fg_color=COLORS["chip_bg"], corner_radius=12)
        box.grid(row=0, column=1, sticky="e", padx=(40, 12))
        ctk.CTkLabel(
            box, text="Bunu mu demek istediniz?",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        wrap = ctk.CTkFrame(box, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))
        for i, s in enumerate(items):
            ctk.CTkButton(
                wrap, text=s, height=28, width=200, text_color="white",
                fg_color=COLORS["btn_fg"], hover_color=COLORS["btn_hover"],
                command=lambda q=s: on_click(q)
            ).grid(row=0, column=i, padx=6, pady=6, sticky="w")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x720")
        self.minsize(980, 640)
        ATTACH_DIR.mkdir(exist_ok=True)

        
        self.font_body = ctk.CTkFont(size=13)
        self.font_small = ctk.CTkFont(size=12)

        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

        
        self._last_resize = 0
        self.bind("<Configure>", self._on_resize)

        
        self._show_welcome_inside_chat()

    
    def _build_sidebar(self):
        s = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0)
        s.grid(row=0, column=0, sticky="nsw")
        for i in range(40): s.grid_rowconfigure(i, weight=0)
        s.grid_rowconfigure(99, weight=1)

        if exists(LOGO_FILE):
            try:
                img = Image.open(LOGO_FILE)
                w, h = img.size
                W = 180; H = int(W * h / w)
                self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(W, H))
                ctk.CTkLabel(s, image=self.logo_img, text="").grid(row=0, column=0, padx=14, pady=(14, 6))
            except:
                ctk.CTkLabel(s, text="Çimsa", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=16, pady=(18, 6))
        else:
            ctk.CTkLabel(s, text="Çimsa", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=16, pady=(18, 6))

        ctk.CTkLabel(s, text="Akıllı Asistan", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=("#26425C", "#A7C8E8")).grid(row=1, column=0, padx=16, pady=(0, 10))
        
        self._section_header(s, "Hızlı Erişim", row=2)
        quick_actions = [
            ("VPN Sorunu", "vpn bağlanmıyor"),
            ("Outlook Şifre", "outlook şifremi unuttum"),
            ("SAP Giriş", "sap giremiyorum"),
            ("Yazıcı", "yazıcı çalışmıyor"),
            ("OneDrive", "onedrive senkronize etmiyor"),
            ("Teams", "teams mikrofon çalışmıyor"),
            ("Talep Aç", "talep açmak istiyorum"),
            ("Ekran Görüntüsü Ekle", "__ATTACH__"),
        ]
        r = 3
        for label, payload in quick_actions:
            self._nav_button(s, label, payload).grid(row=r, column=0, padx=16, pady=4, sticky="ew")
            r += 1

        self._section_header(s, "Kurumsal Bilgi", row=r); r += 1
        corp_actions = [
            ("Misyon & Vizyon", "çimsa misyon vizyon"),
            ("Web Sitesi", "çimsa internet sitesi"),
            ("Kuruluş / Tarihçe", "çimsa ne zaman kuruldu"),
            ("Sürdürülebilirlik", "çimsa sürdürülebilirlik"),
            ("IT Departmanı Yeri", "bilgi teknoloji departmanı nerede"),
            ("Çimsa CEO", "çimsa ceo"),
            ("Sabancı Geçmişi", "sabancı geçmişi"),
        ]
        for label, payload in corp_actions:
            self._nav_button(s, label, payload).grid(row=r, column=0, padx=16, pady=4, sticky="ew")
            r += 1

    def _section_header(self, parent, text, row):
        bar = ctk.CTkFrame(parent, fg_color=COLORS["section"], corner_radius=6, height=28)
        bar.grid(row=row, column=0, padx=14, pady=(10, 6), sticky="ew")
        bar.grid_propagate(False)
        ctk.CTkLabel(bar, text=text, anchor="w", padx=10,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(fill="both", expand=True)

    def _nav_button(self, parent, label, payload):
        return ctk.CTkButton(
            parent, text=label, width=180, height=34, text_color="white",
            fg_color=COLORS["btn_fg"], hover_color=COLORS["btn_hover"],
            command=lambda p=payload: self._quick_action(p)
        )

    def _build_main(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=0)
        self.main.grid_columnconfigure(0, weight=1)

        self.bg_label = None
        self._load_bg()

        self.chat = ChatArea(self.main, self.font_body, self.font_small)
        self.chat.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 6))

        input_card = ctk.CTkFrame(self.main, fg_color=COLORS["card"], corner_radius=12)
        input_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(4, 10))
        input_card.grid_columnconfigure(0, weight=1)
        input_card.grid_columnconfigure(1, weight=0)

        self.entry = ctk.CTkTextbox(input_card, height=54, fg_color=("white","#101418"), font=self.font_body)
        self.entry.grid(row=0, column=0, padx=(12, 6), pady=10, sticky="ew")
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Shift-Return>", lambda e: None)

        ctk.CTkButton(
            input_card, text="Gönder", width=120, height=46,
            fg_color=COLORS["btn_fg"], hover_color=COLORS["btn_hover"], text_color="white",
            command=self._send
        ).grid(row=0, column=1, padx=(6, 10), pady=10)

    def _show_welcome_inside_chat(self):
        self.chat.add_system_welcome(
            "Merhaba, ben Çimsa Akıllı Asistan 👋  —  IT sorunlarınız ve talepleriniz için buradayım."
        )
        self.chat.add_bot(
            self.chat.add_bot(
    "✍️ Lütfen yaşadığınız sorunu veya ihtiyacınızı buraya yazın.\n"
    "Size adım adım yardımcı olacağım ve gerekli bilgileri sohbet içinde soracağım.\n\n"
    "💡 Dilerseniz doğrudan soldaki **'Talep Aç'** butonuna basarak da talebinizi başlatabilirsiniz."
    )
       )

    def _load_bg(self):
        if not exists(BACKGROUND_FILE):
            return
        try:
            img = Image.open(BACKGROUND_FILE).convert("RGB")
            img = img.filter(ImageFilter.GaussianBlur(radius=8))
            img = img.point(lambda p: int(p * 0.65))
            w = max(self.winfo_width(), 1180)
            h = max(self.winfo_height(), 620)
            self._bg_raw = img
            self._bg_img = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
            if self.bg_label is None:
                self.bg_label = ctk.CTkLabel(self.main, image=self._bg_img, text="")
                self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                self.bg_label.configure(image=self._bg_img)
        except Exception as e:
            print("[BG WARN]", e)
            self.bg_label = None

    def _on_resize(self, event):
        now = time.time()
        if not hasattr(self, "_last_resize") or now - self._last_resize < 0.12:
            return
        self._last_resize = now
        if self.bg_label and hasattr(self, "_bg_raw"):
            try:
                w = max(self.main.winfo_width(), 800)
                h = max(self.main.winfo_height(), 600)
                self._bg_img = ctk.CTkImage(light_image=self._bg_raw, dark_image=self._bg_raw, size=(w, h))
                self.bg_label.configure(image=self._bg_img)
            except Exception as e:
                print("[BG RESIZE]", e)


    def _quick_action(self, payload: str):
        if payload == "__ATTACH__":
            fp = fd.askopenfilename(
                title="Ekran görüntüsü / dosya seç",
                filetypes=[("Görseller", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"), ("Tümü", "*.*")]
            )
            if not fp: return
            src = Path(fp); dest = ATTACH_DIR / src.name
            try:
                dest.write_bytes(src.read_bytes())
                self.chat.add_bot(f"📎 Dosya eklendi: {dest.name}")
                reply = get_bot_response(f"__ATTACH__::{dest.name}")
                if reply: self._append_bot(reply)
            except Exception as e:
                self.chat.add_bot("⚠️ Dosya eklenirken hata oluştu.")
                print("[ATTACH]", e)
            return

        self._append_user(payload)
        self._append_bot(get_bot_response(payload))

    def _on_enter(self, event):
        if event.state & 0x0001:  
            return
        self._send()
        return "break"

    def _send(self):
        text = self.entry.get("1.0", "end").strip()
        if not text: return
        self._append_user(text)
        try:
            reply = get_bot_response(text)
        except Exception as e:
            reply = "⚠️ Bir hata oluştu. Lütfen tekrar deneyin."
            print("[BOT]", e)
        self._append_bot(reply)
        self.entry.delete("1.0", "end")

    def _append_user(self, msg: str):
        self.chat.add_user(msg)

    def _append_bot(self, msg: str):
        if isinstance(msg, str) and msg.startswith("SUGGEST|"):
            items = [s for s in msg.split("|")[1:] if s.strip()]
            if items:
                self.chat.add_suggestions(items, self._quick_action)
            return
        self.chat.add_bot(msg)

if __name__ == "__main__":
    app = App()
    app.mainloop()
