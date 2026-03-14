from screeninfo import get_monitors
import colorsys
import tkinter as tk
from dataclasses import dataclass
from typing import Optional, Tuple

from PIL import ImageGrab


@dataclass
class Region:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return (self.left, self.top, self.right, self.bottom)

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)


def clamp_u8(value: float) -> int:
    return max(0, min(255, int(round(value))))


def average_color(image) -> Tuple[int, int, int]:
    small = image.resize((16, 16))
    pixels = list(small.getdata())
    r = sum(p[0] for p in pixels) / len(pixels)
    g = sum(p[1] for p in pixels) / len(pixels)
    b = sum(p[2] for p in pixels) / len(pixels)
    return clamp_u8(r), clamp_u8(g), clamp_u8(b)


def center_pixel_color(image) -> Tuple[int, int, int]:
    w, h = image.size
    x = max(0, w // 2)
    y = max(0, h // 2)
    p = image.getpixel((x, y))
    return int(p[0]), int(p[1]), int(p[2])


def most_saturated_pixel_color(image) -> Tuple[int, int, int]:
    small = image.resize((48, 48))
    best_rgb = (0, 0, 0)
    best_sat = -1.0
    best_value = -1.0

    for r, g, b in small.getdata():
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s > best_sat or (abs(s - best_sat) < 1e-6 and v > best_value):
            best_sat = s
            best_value = v
            best_rgb = (int(r), int(g), int(b))

    return best_rgb


def rgb_to_english_name(rgb: Tuple[int, int, int], lang: str = "English") -> str:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

    # Translation dictionaries
    descriptors = {
        "English": {
            "very dark": "very dark", "dark": "dark", "bright": "bright", "muted": "muted", "soft": "soft", "pale": "pale", "warm": "warm", "cool": "cool", "neon": "neon", "vivid": "vivid", "pastel": "pastel", "deep": "deep", "black": "black", "gray": "gray", "dark gray": "dark gray", "light gray": "light gray", "white": "white"
        },
        "Spanish": {
            "very dark": "muy oscuro", "dark": "oscuro", "bright": "brillante", "muted": "apagado", "soft": "suave", "pale": "pálido", "warm": "cálido", "cool": "frío", "neon": "neón", "vivid": "vivo", "pastel": "pastel", "deep": "profundo", "black": "negro", "gray": "gris", "dark gray": "gris oscuro", "light gray": "gris claro", "white": "blanco"
        },
        "French": {
            "very dark": "très foncé", "dark": "foncé", "bright": "brillant", "muted": "terne", "soft": "doux", "pale": "pâle", "warm": "chaud", "cool": "froid", "neon": "néon", "vivid": "vif", "pastel": "pastel", "deep": "profond", "black": "noir", "gray": "gris", "dark gray": "gris foncé", "light gray": "gris clair", "white": "blanc"
        },
        "German": {
            "very dark": "sehr dunkel", "dark": "dunkel", "bright": "hell", "muted": "gedämpft", "soft": "weich", "pale": "blass", "warm": "warm", "cool": "kühl", "neon": "neon", "vivid": "lebhaft", "pastel": "pastell", "deep": "tief", "black": "schwarz", "gray": "grau", "dark gray": "dunkelgrau", "light gray": "hellgrau", "white": "weiß"
        },
        "Chinese (Simplified)": {
            "very dark": "很深", "dark": "深", "bright": "亮", "muted": "柔和", "soft": "柔软", "pale": "浅", "warm": "暖", "cool": "冷", "neon": "霓虹", "vivid": "鲜艳", "pastel": "淡色", "deep": "深邃", "black": "黑色", "gray": "灰色", "dark gray": "深灰色", "light gray": "浅灰色", "white": "白色"
        },
        "Hindi": {
            "very dark": "बहुत गहरा", "dark": "गहरा", "bright": "चमकीला", "muted": "म्लान", "soft": "मुलायम", "pale": "फीका", "warm": "गर्म", "cool": "ठंडा", "neon": "नियॉन", "vivid": "चटख", "pastel": "पेस्टल", "deep": "गहरा", "black": "काला", "gray": "धूसर", "dark gray": "गहरा धूसर", "light gray": "हल्का धूसर", "white": "सफेद"
        },
        "Arabic": {
            "very dark": "داكن جدًا", "dark": "داكن", "bright": "ساطع", "muted": "هادئ", "soft": "ناعم", "pale": "باهت", "warm": "دافئ", "cool": "بارد", "neon": "نيون", "vivid": "زاهي", "pastel": "باستيل", "deep": "عميق", "black": "أسود", "gray": "رمادي", "dark gray": "رمادي داكن", "light gray": "رمادي فاتح", "white": "أبيض"
        },
        "Portuguese": {
            "very dark": "muito escuro", "dark": "escuro", "bright": "brilhante", "muted": "suave", "soft": "macio", "pale": "pálido", "warm": "quente", "cool": "frio", "neon": "neon", "vivid": "vivo", "pastel": "pastel", "deep": "profundo", "black": "preto", "gray": "cinza", "dark gray": "cinza escuro", "light gray": "cinza claro", "white": "branco"
        },
        "Russian": {
            "very dark": "очень темный", "dark": "темный", "bright": "яркий", "muted": "приглушенный", "soft": "мягкий", "pale": "бледный", "warm": "теплый", "cool": "холодный", "neon": "неоновый", "vivid": "насыщенный", "pastel": "пастельный", "deep": "глубокий", "black": "черный", "gray": "серый", "dark gray": "темно-серый", "light gray": "светло-серый", "white": "белый"
        },
        "Japanese": {
            "very dark": "とても暗い", "dark": "暗い", "bright": "明るい", "muted": "くすんだ", "soft": "やわらかい", "pale": "淡い", "warm": "暖かい", "cool": "涼しい", "neon": "ネオン", "vivid": "鮮やか", "pastel": "パステル", "deep": "深い", "black": "黒", "gray": "灰色", "dark gray": "濃い灰色", "light gray": "薄い灰色", "white": "白"
        },
        "Italian": {
            "very dark": "molto scuro", "dark": "scuro", "bright": "luminoso", "muted": "smorzato", "soft": "morbido", "pale": "pallido", "warm": "caldo", "cool": "freddo", "neon": "neon", "vivid": "vivido", "pastel": "pastello", "deep": "profondo", "black": "nero", "gray": "grigio", "dark gray": "grigio scuro", "light gray": "grigio chiaro", "white": "bianco"
        },
        "Korean": {
            "very dark": "매우 어두운", "dark": "어두운", "bright": "밝은", "muted": "부드러운", "soft": "부드러운", "pale": "연한", "warm": "따뜻한", "cool": "차가운", "neon": "네온", "vivid": "선명한", "pastel": "파스텔", "deep": "깊은", "black": "검정", "gray": "회색", "dark gray": "진한 회색", "light gray": "연한 회색", "white": "흰색"
        },
        "Turkish": {
            "very dark": "çok koyu", "dark": "koyu", "bright": "parlak", "muted": "soluk", "soft": "yumuşak", "pale": "açık", "warm": "sıcak", "cool": "soğuk", "neon": "neon", "vivid": "canlı", "pastel": "pastel", "deep": "derin", "black": "siyah", "gray": "gri", "dark gray": "koyu gri", "light gray": "açık gri", "white": "beyaz"
        },
        "Dutch": {
            "very dark": "zeer donker", "dark": "donker", "bright": "helder", "muted": "gedempt", "soft": "zacht", "pale": "bleek", "warm": "warm", "cool": "koel", "neon": "neon", "vivid": "levendig", "pastel": "pastel", "deep": "diep", "black": "zwart", "gray": "grijs", "dark gray": "donkergrijs", "light gray": "lichtgrijs", "white": "wit"
        }
    }
    hues = {
        "English": [
            "red", "red-orange", "orange", "yellow-orange", "yellow", "yellow-green", "green", "spring green", "cyan", "sky blue", "blue", "violet", "magenta", "rose"
        ],
        "Spanish": [
            "rojo", "rojo anaranjado", "naranja", "naranja amarillento", "amarillo", "amarillo verdoso", "verde", "verde primavera", "cian", "azul cielo", "azul", "violeta", "magenta", "rosa"
        ],
        "French": [
            "rouge", "rouge-orangé", "orange", "orange-jaune", "jaune", "jaune-vert", "vert", "vert printemps", "cyan", "bleu ciel", "bleu", "violet", "magenta", "rose"
        ],
        "German": [
            "rot", "rot-orange", "orange", "gelb-orange", "gelb", "gelb-grün", "grün", "frühlingsgrün", "cyan", "himmelblau", "blau", "violett", "magenta", "rosa"
        ],
        "Chinese (Simplified)": [
            "红色", "红橙色", "橙色", "黄橙色", "黄色", "黄绿色", "绿色", "春绿色", "青色", "天蓝色", "蓝色", "紫色", "品红", "玫红"
        ],
        "Hindi": [
            "लाल", "लाल-नारंगी", "नारंगी", "पीला-नारंगी", "पीला", "पीला-हरा", "हरा", "वसंत हरा", " सियान", "आकाश नीला", "नीला", "बैंगनी", "मैजेंटा", "गुलाबी"
        ],
        "Arabic": [
            "أحمر", "أحمر برتقالي", "برتقالي", "برتقالي أصفر", "أصفر", "أصفر أخضر", "أخضر", "ربيعي أخضر", "سماوي", "أزرق سماوي", "أزرق", "بنفسجي", "ماجنتا", "وردي"
        ],
        "Portuguese": [
            "vermelho", "vermelho-alaranjado", "laranja", "laranja-amarelo", "amarelo", "amarelo-esverdeado", "verde", "verde primavera", "ciano", "azul céu", "azul", "violeta", "magenta", "rosa"
        ],
        "Russian": [
            "красный", "красно-оранжевый", "оранжевый", "желто-оранжевый", "желтый", "желто-зеленый", "зеленый", "весенний зеленый", "циан", "небесно-голубой", "синий", "фиолетовый", "маджента", "розовый"
        ],
        "Japanese": [
            "赤", "赤橙", "橙", "黄橙", "黄", "黄緑", "緑", "春緑", "シアン", "空色", "青", "紫", "マゼンタ", "ローズ"
        ],
        "Italian": [
            "rosso", "rosso-arancione", "arancione", "giallo-arancione", "giallo", "giallo-verde", "verde", "verde primavera", "ciano", "blu cielo", "blu", "viola", "magenta", "rosa"
        ],
        "Korean": [
            "빨강", "빨강-주황", "주황", "노랑-주황", "노랑", "노랑-초록", "초록", "봄초록", "청록", "하늘색", "파랑", "보라", "마젠타", "장미"
        ],
        "Turkish": [
            "kırmızı", "kırmızı-turuncu", "turuncu", "sarı-turuncu", "sarı", "sarı-yeşil", "yeşil", "bahar yeşili", "camgöbeği", "gök mavisi", "mavi", "mor", "macenta", "pembe"
        ],
        "Dutch": [
            "rood", "rood-oranje", "oranje", "geel-oranje", "geel", "geel-groen", "groen", "lentegroen", "cyaan", "hemelsblauw", "blauw", "violet", "magenta", "roze"
        ]
    }

    if v < 0.08:
        return descriptors[lang]["black"]

    if s < 0.10:
        if v < 0.25:
            return descriptors[lang]["dark gray"]
        if v < 0.75:
            return descriptors[lang]["gray"]
        if v < 0.93:
            return descriptors[lang]["light gray"]
        return descriptors[lang]["white"]

    hue_deg = h * 360
    hue_boundaries = [0, 15, 35, 50, 65, 85, 145, 170, 200, 220, 250, 280, 315, 340, 360]
    hue_labels = hues[lang]
    hue_label = hue_labels[0]
    for i, boundary in enumerate(hue_boundaries):
        if hue_deg <= boundary:
            hue_label = hue_labels[i]
            break

    modifiers = []

    # Value/brightness descriptors
    if v < 0.20:
        modifiers.append(descriptors[lang]["very dark"])
    elif v < 0.40:
        modifiers.append(descriptors[lang]["dark"])
    elif v > 0.85 and s > 0.60:
        modifiers.append(descriptors[lang]["bright"])

    # Saturation descriptors
    if s < 0.28:
        modifiers.append(descriptors[lang]["muted"])
    elif s < 0.45 and v > 0.65:
        modifiers.append(descriptors[lang]["soft"])

    if v > 0.90 and s < 0.35:
        modifiers.append(descriptors[lang]["pale"])

    # Temperature descriptors
    if hue_label in [hue_labels[0], hue_labels[1], hue_labels[2], hue_labels[3], hue_labels[4], hue_labels[12]]:
        if s > 0.45 and v > 0.45:
            modifiers.append(descriptors[lang]["warm"])
    elif hue_label in [hue_labels[10], hue_labels[11], hue_labels[8], hue_labels[9], hue_labels[5], hue_labels[6], hue_labels[7]]:
        if s > 0.45 and v > 0.45:
            modifiers.append(descriptors[lang]["cool"])

    # Special descriptors
    if s > 0.85 and v > 0.85:
        modifiers.append(descriptors[lang]["neon"])
    elif s > 0.75 and v > 0.75:
        modifiers.append(descriptors[lang]["vivid"])
    elif s < 0.25 and v > 0.85:
        modifiers.append(descriptors[lang]["pastel"])
    elif s > 0.65 and v < 0.35:
        modifiers.append(descriptors[lang]["deep"])

    return " ".join(modifiers + [hue_label]).strip()


class RegionSelector(tk.Toplevel):
    def __init__(self, master, on_done):
        super().__init__(master)
        self.on_done = on_done
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        self.canvas = tk.Canvas(self, cursor="cross", bg="black", highlightthickness=0)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.28)

        # Multi-monitor support: create overlay covering all monitors
        monitors = get_monitors()
        min_x = min(m.x for m in monitors)
        min_y = min(m.y for m in monitors)
        max_x = max(m.x + m.width for m in monitors)
        max_y = max(m.y + m.height for m in monitors)
        print(f"DEBUG: Virtual screen: left={min_x}, top={min_y}, right={max_x}, bottom={max_y}")
        self.geometry(f"{max_x - min_x}x{max_y - min_y}+{min_x}+{min_y}")
        self.virtual_offset_x = min_x
        self.virtual_offset_y = min_y

        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_press(self, event):
        # event.x_root and event.y_root are absolute screen coordinates
        # event.x and event.y are relative to overlay
        self.start_x = event.x + self.virtual_offset_x
        self.start_y = event.y + self.virtual_offset_y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="white", width=2
        )

    def on_drag(self, event):
        if not self.rect_id:
            return
        self.canvas.coords(self.rect_id, self.start_x - self.virtual_offset_x, self.start_y - self.virtual_offset_y, event.x, event.y)

    def on_release(self, event):
        # Use absolute screen coordinates
        end_x = event.x + self.virtual_offset_x
        end_y = event.y + self.virtual_offset_y
        left = min(self.start_x, end_x)
        right = max(self.start_x, end_x)
        top = min(self.start_y, end_y)
        bottom = max(self.start_y, end_y)

        if right - left < 3 or bottom - top < 3:
            self.destroy()
            return

        self.on_done(Region(left, top, right, bottom))
        self.destroy()


class ColorGuesserApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Approximate Color Guesser")
        self.root.geometry("460x330")

        self.region: Optional[Region] = None
        self.running = False
        self.after_id = None

        self.interval_ms = tk.IntVar(value=250)
        self.sample_mode = tk.StringVar(value="Center pixel")
        self.language = tk.StringVar(value="English")

        self.region_var = tk.StringVar(value="No region selected")
        self.hex_var = tk.StringVar(value="#000000")
        self.rgb_var = tk.StringVar(value="RGB: (0, 0, 0)")
        self.name_var = tk.StringVar(value="Approximate color: black")

        self.build_ui()


    def build_ui(self):
        frame = tk.Frame(self.root, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Approximate Color Guesser", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(frame, text="Select a region where your app shows the active color.", fg="#555").pack(anchor="w", pady=(0, 10))

        top_row = tk.Frame(frame)
        top_row.pack(fill="x", pady=(0, 8))

        tk.Button(top_row, text="Select Region", command=self.select_region).pack(side="left")
        tk.Button(top_row, text="Preview Region", command=self.preview_region).pack(side="left", padx=6)
        tk.Button(top_row, text="Start Monitoring", command=self.start).pack(side="left", padx=6)
        tk.Button(top_row, text="Stop", command=self.stop).pack(side="left")

        tk.Label(frame, textvariable=self.region_var, anchor="w").pack(fill="x", pady=(0, 8))

        settings = tk.Frame(frame)
        settings.pack(fill="x", pady=(0, 10))

        tk.Label(settings, text="Sampling mode:").grid(row=0, column=0, sticky="w")
        tk.OptionMenu(settings, self.sample_mode, "Center pixel", "Average region", "Most saturated pixel").grid(
            row=0,
            column=1,
            sticky="w",
            padx=(8, 16),
        )

        tk.Label(settings, text="Interval (ms):").grid(row=0, column=2, sticky="w")
        tk.Spinbox(settings, from_=100, to=2000, increment=50, textvariable=self.interval_ms, width=6).grid(
            row=0,
            column=3,
            sticky="w",
            padx=(8, 0),
        )

        tk.Label(settings, text="Language:").grid(row=0, column=4, sticky="w", padx=(16, 0))
        tk.OptionMenu(settings, self.language,
            "English", "Spanish", "French", "German", "Chinese (Simplified)", "Hindi", "Arabic", "Portuguese", "Russian", "Japanese", "Italian", "Korean", "Turkish", "Dutch"
        ).grid(
            row=0,
            column=5,
            sticky="w",
            padx=(8, 0),
        )

        swatch_row = tk.Frame(frame)
        swatch_row.pack(fill="x", pady=(6, 4))

        self.swatch = tk.Canvas(swatch_row, width=56, height=56, highlightthickness=1, highlightbackground="#333")
        self.swatch.pack(side="left")
        self.swatch_rect = self.swatch.create_rectangle(0, 0, 56, 56, fill="#000000", outline="")

        info = tk.Frame(swatch_row)
        info.pack(side="left", padx=10)
        tk.Label(info, textvariable=self.hex_var, font=("Consolas", 12, "bold")).pack(anchor="w")
        tk.Label(info, textvariable=self.rgb_var).pack(anchor="w")

        tk.Label(frame, textvariable=self.name_var, font=("Segoe UI", 13, "bold"), pady=8).pack(anchor="w")

        help_text = (
            "Tip: choose a small region around your app's color preview for best results."
        )
        tk.Label(frame, text=help_text, fg="#444", wraplength=430, justify="left").pack(anchor="w", pady=(6, 0))

    def preview_region(self):
        if not self.region:
            self.name_var.set("Approximate color: (select region first)")
            return
        try:
            image = ImageGrab.grab(bbox=self.region.bbox)
        except Exception as exc:
            self.name_var.set(f"Preview error: {exc}")
            return
        preview = tk.Toplevel(self.root)
        preview.title("Region Preview")
        preview.geometry(f"{image.width}x{image.height}")
        preview_canvas = tk.Canvas(preview, width=image.width, height=image.height)
        preview_canvas.pack()
        # Convert PIL image to Tkinter PhotoImage
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(image)
        preview_canvas.create_image(0, 0, anchor="nw", image=photo)
        preview_canvas.image = photo  # Prevent garbage collection
        preview.lift()

    def select_region(self):
        self.root.withdraw()

        def done(region: Region):
            print(f"DEBUG: Selected region: left={region.left}, top={region.top}, right={region.right}, bottom={region.bottom}")
            self.region = region
            self.region_var.set(
                f"Region: left={region.left}, top={region.top}, right={region.right}, bottom={region.bottom}"
            )
            self.root.deiconify()
            self.root.lift()

        def on_close_restore():
            self.root.deiconify()
            self.root.lift()

        selector = RegionSelector(self.root, done)
        selector.protocol("WM_DELETE_WINDOW", lambda: (selector.destroy(), on_close_restore()))

    def start(self):
        if not self.region:
            self.name_var.set("Approximate color: (select region first)")
            return
        if self.running:
            return
        self.running = True
        self.tick()

    def stop(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def sample_region(self, region: Region) -> Tuple[int, int, int]:
        image = ImageGrab.grab(bbox=region.bbox)
        mode = self.sample_mode.get()
        if mode == "Average region":
            rgb = average_color(image)
        elif mode == "Most saturated pixel":
            rgb = most_saturated_pixel_color(image)
        else:
            rgb = center_pixel_color(image)
        return rgb

    def update_display(self, rgb: Tuple[int, int, int]):
        r, g, b = rgb
        hex_code = f"#{r:02X}{g:02X}{b:02X}"
        self.hex_var.set(hex_code)
        self.rgb_var.set(f"RGB: ({r}, {g}, {b})")
        lang = self.language.get()
        self.name_var.set(f"Approximate color: {rgb_to_english_name(rgb, lang)}")
        self.swatch.itemconfig(self.swatch_rect, fill=hex_code)

    def tick(self):
        if not self.running or not self.region:
            return

        try:
            rgb = self.sample_region(self.region)
            self.update_display(rgb)
        except Exception as exc:
            self.name_var.set(f"Approximate color: error ({exc})")

        interval = max(100, int(self.interval_ms.get()))
        self.after_id = self.root.after(interval, self.tick)


def main():
    root = tk.Tk()
    app = ColorGuesserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
