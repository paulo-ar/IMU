import sqlite3
import time
import serial
import tkinter as tk
from datetime import datetime
from pathlib import Path
from threading import Event, Thread
from tkinter import ttk
from tkinter import font as tkfont


COLORS = {
    "navy": "#062A4F",
    "navy_2": "#0A3A67",
    "navy_3": "#123F67",
    "turquoise": "#00B8C8",
    "turquoise_dark": "#0097A7",
    "turquoise_light": "#E7FBFD",
    "green": "#35D05C",
    "green_dark": "#1E9F45",
    "red": "#E53946",
    "red_dark": "#B92530",
    "white": "#FFFFFF",
    "off_white": "#F5F8FB",
    "line": "#D8E5EE",
    "muted": "#6B7A8A",
    "pending": "#E9EEF3",
}

FONT_FAMILY = "Montserrat"
FALLBACK_FONTS = ("Montserrat", "Roboto", "Lato", "Segoe UI", "Helvetica")
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def modern_font(size=10, weight="normal"):
    return (FONT_FAMILY, size, weight)


def configure_global_style(root):
    global FONT_FAMILY
    available_fonts = set(tkfont.families(root))
    FONT_FAMILY = next(
        (font_name for font_name in FALLBACK_FONTS if font_name in available_fonts),
        "Segoe UI",
    )

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=COLORS["off_white"])
    root.option_add("*Font", modern_font(10))
    root.option_add("*Entry.Font", modern_font(10))
    root.option_add("*Button.Font", modern_font(10, "bold"))

    style.configure(".", font=modern_font(10), background=COLORS["off_white"])
    style.configure("App.TFrame", background=COLORS["off_white"])
    style.configure("Surface.TFrame", background=COLORS["white"])
    style.configure("Header.TFrame", background=COLORS["navy"])
    style.configure("HeaderLogo.TFrame", background=COLORS["white"])
    style.configure("TLabel", background=COLORS["off_white"], foreground=COLORS["navy"])
    style.configure("Surface.TLabel", background=COLORS["white"], foreground=COLORS["navy"])
    style.configure("AppLogo.TLabel", background=COLORS["off_white"], foreground=COLORS["navy"])
    style.configure("Title.TLabel", font=modern_font(34, "bold"), foreground=COLORS["navy"])
    style.configure("TabTitle.TLabel", font=modern_font(22, "bold"), foreground=COLORS["navy"])
    style.configure("HeaderTitle.TLabel", font=("Segoe UI Semibold", 46, "bold"), background=COLORS["navy"], foreground=COLORS["white"])
    style.configure("HeaderDefinition.TLabel", font=modern_font(11, "bold"), background=COLORS["navy"], foreground="#D9F7FA")
    style.configure("HeaderCredit.TLabel", font=modern_font(8), background=COLORS["navy"], foreground="#A9DDE5")
    style.configure("Subtitle.TLabel", font=modern_font(9), foreground=COLORS["muted"])
    style.configure("HeaderSubtitle.TLabel", font=modern_font(9), background=COLORS["navy"], foreground="#CDEBF0")
    style.configure("Section.TLabel", font=modern_font(13, "bold"), foreground=COLORS["navy"])
    style.configure("Logo.TLabel", font=modern_font(8, "bold"), background=COLORS["white"], foreground=COLORS["navy"], padding=(10, 6))

    style.configure("Modern.TEntry", fieldbackground=COLORS["white"], foreground=COLORS["navy"], bordercolor=COLORS["line"], lightcolor=COLORS["turquoise"], darkcolor=COLORS["line"], padding=(10, 8), insertcolor=COLORS["turquoise"])
    style.map("Modern.TEntry", bordercolor=[("focus", COLORS["turquoise"])], lightcolor=[("focus", COLORS["turquoise"])])
    style.configure("Modern.TCombobox", fieldbackground=COLORS["white"], foreground=COLORS["navy"], bordercolor=COLORS["line"], arrowcolor=COLORS["turquoise"], padding=(8, 7))
    style.map("Modern.TCombobox", bordercolor=[("focus", COLORS["turquoise"])])

    style.configure("Accent.TButton", font=modern_font(10, "bold"), foreground=COLORS["white"], background=COLORS["turquoise"], borderwidth=0, focusthickness=0, padding=(16, 9))
    style.map("Accent.TButton", background=[("active", COLORS["turquoise_dark"]), ("pressed", COLORS["navy_2"])], foreground=[("disabled", "#DDE8EF")])
    style.configure("Ghost.TButton", font=modern_font(10, "bold"), foreground=COLORS["turquoise"], background=COLORS["white"], bordercolor=COLORS["turquoise"], borderwidth=1, padding=(16, 9))
    style.map("Ghost.TButton", background=[("active", COLORS["turquoise_light"])], foreground=[("active", COLORS["navy"])])
    style.configure("Exit.TButton", font=modern_font(9, "bold"), foreground=COLORS["white"], background=COLORS["navy_2"], borderwidth=0, padding=(14, 8))
    style.map("Exit.TButton", background=[("active", COLORS["red_dark"]), ("pressed", COLORS["red"])])

    style.configure("TNotebook", background=COLORS["off_white"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        font=modern_font(10, "bold"),
        background="#DCEAF2",
        foreground=COLORS["navy"],
        padding=(30, 12),
        width=14,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["turquoise"]), ("active", "#DCEAF2")],
        foreground=[("selected", COLORS["white"]), ("active", COLORS["navy"])],
    )

    style.configure("Modern.Treeview", font=modern_font(9), rowheight=30, background=COLORS["white"], fieldbackground=COLORS["white"], foreground=COLORS["navy"], borderwidth=0)
    style.configure("Modern.Treeview.Heading", font=modern_font(9, "bold"), background=COLORS["navy"], foreground=COLORS["white"], padding=(8, 8), relief="flat")
    style.map("Modern.Treeview.Heading", background=[("active", COLORS["navy_2"])])
    style.map("Modern.Treeview", background=[("selected", COLORS["turquoise"])], foreground=[("selected", COLORS["white"])])

    style.configure("Modern.TCheckbutton", background=COLORS["white"], foreground=COLORS["navy"], font=modern_font(10, "bold"), padding=(8, 6))
    style.map("Modern.TCheckbutton", foreground=[("selected", COLORS["green_dark"])])

    style.configure("TSeparator", background=COLORS["line"])
    return style


class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command, width=220, height=42, radius=18):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=COLORS["white"],
            highlightthickness=0,
            cursor="hand2",
        )
        self.command = command
        self.width = width
        self.height = height
        self.radius = radius
        self.normal_color = COLORS["turquoise"]
        self.hover_color = COLORS["turquoise_dark"]
        self._draw(text, self.normal_color)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda _event: self._draw(text, self.hover_color))
        self.bind("<Leave>", lambda _event: self._draw(text, self.normal_color))

    def _draw(self, text, color):
        self.delete("all")
        r = self.radius
        w = self.width
        h = self.height
        self.create_arc(0, 0, r * 2, r * 2, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w - r * 2, 0, w, r * 2, start=0, extent=90, fill=color, outline=color)
        self.create_arc(0, h - r * 2, r * 2, h, start=180, extent=90, fill=color, outline=color)
        self.create_arc(w - r * 2, h - r * 2, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w - r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h - r, fill=color, outline=color)
        self.create_text(w / 2, h / 2, text=text, fill=COLORS["white"], font=modern_font(10, "bold"))

    def _on_click(self, _event):
        self.command()


class LogoStrip(ttk.Frame):
    def __init__(self, master, style="Surface.TFrame", compact=False, max_height=None):
        super().__init__(master, style=style)
        self.images = []
        if style == "Header.TFrame":
            self.label_style = "HeaderSubtitle.TLabel"
        elif style == "HeaderLogo.TFrame":
            self.label_style = "Surface.TLabel"
        elif style == "App.TFrame":
            self.label_style = "AppLogo.TLabel"
        else:
            self.label_style = "Surface.TLabel"
        self._add_logo("logos.png", "Logos", compact, max_height)

    def _add_logo(self, filename, fallback_text, compact, max_height):
        logo_path = ASSETS_DIR / filename
        if logo_path.exists():
            image = tk.PhotoImage(file=str(logo_path))
            target_height = max_height or (58 if compact else 72)
            scale = max(1, (image.height() + target_height - 1) // target_height)
            if scale > 1:
                image = image.subsample(scale, scale)
            self.images.append(image)
            ttk.Label(self, image=image, style=self.label_style).pack(side="left")
        else:
            ttk.Label(self, text=fallback_text, style=self.label_style).pack(side="left")

# ==========================================
# 1. BASE DE DATOS (SQLite3)
# ==========================================
conn = sqlite3.connect("satms.db", check_same_thread=False)
cursor = conn.cursor()


def init_db():
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_incubadora TEXT,
        id_torquimetro TEXT,
        id_usuario TEXT,
        nombre_usuario TEXT,
        id_paso INTEGER,
        id_campo INTEGER,
        alignment_not_aligned INTEGER DEFAULT 0,
        fecha_inicio TEXT,
        fecha_fin TEXT
    )
    """
    )
    conn.commit()

    cursor.execute("PRAGMA table_info(registros)")
    columnas = [fila[1] for fila in cursor.fetchall()]
    if "alignment_not_aligned" not in columnas:
        cursor.execute(
            "ALTER TABLE registros ADD COLUMN alignment_not_aligned INTEGER DEFAULT 0"
        )
        conn.commit()


def insertar_inicio(data, paso, campo, alignment_not_aligned):
    cursor.execute(
        """
    INSERT INTO registros
    (id_incubadora, id_torquimetro, id_usuario, nombre_usuario, id_paso, id_campo, alignment_not_aligned, fecha_inicio)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (*data, paso, campo, alignment_not_aligned, datetime.now()),
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_fin(id_registro):
    cursor.execute(
        """
    UPDATE registros SET fecha_fin = ? WHERE id = ?
    """,
        (datetime.now(), id_registro),
    )
    conn.commit()


def obtener_registros(id_incubadora=None):
    if id_incubadora:
        cursor.execute(
            "SELECT * FROM registros WHERE id_incubadora LIKE ? ORDER BY id DESC",
            (f"%{id_incubadora}%",),
        )
    else:
        cursor.execute("SELECT * FROM registros ORDER BY id DESC")
    return cursor.fetchall()


# ==========================================
# 2. BLUETOOTH
# ==========================================
class Bluetooth:
    def __init__(self, puerto="COM6"):
        self.ser = serial.Serial(puerto, 9600, timeout=1)

    def enviar(self, valor):
        self.ser.write((str(valor) + "\n").encode())

    def leer(self):
        if self.ser.in_waiting:
            return self.ser.readline().decode().strip()
        return None


# ==========================================
# 3. CONTROL DE PROCESO
# ==========================================
class Proceso:
    def __init__(self, bluetooth, data_usuario, callback_ui, toggle_callback):
        self.bt = bluetooth
        self.data = data_usuario
        self.callback_ui = callback_ui
        self.toggle_callback = toggle_callback  # Para verificar el toggle
        self.detener_evento = Event()

        # Llamadas por paso.
        self.campos_paso_1 = [3, 4, 5]
        self.campos_paso_2 = [2, 3, 5]  # Renombrado de paso 3 a paso 2

    def ejecutar(self):
        if not self.ejecutar_paso_1():
            return
        # Esperar toggle para iniciar paso 2
        while not self.detener_evento.is_set():
            if self.toggle_callback():
                if not self.ejecutar_paso_2():
                    return
                break
            time.sleep(0.1)
        self.callback_ui("proceso_finalizado", 2)

    def ejecutar_paso_1(self):
        for campo, segundos in enumerate(self.campos_paso_1, start=1):
            if not self.ejecutar_campo(1, campo, segundos):
                return False
        return True

    def ejecutar_paso_2(self):
        campos = [2, 3, 5]
        for i, segundos in enumerate(campos, start=1):
            campo = i
            if not self.ejecutar_campo(2, campo, segundos):
                return False
            # Después de completar, si no es el último, esperar toggle para el siguiente
            if i < 3:
                while not self.detener_evento.is_set():
                    if self.toggle_callback():
                        break
                    time.sleep(0.1)
                if self.detener_evento.is_set():
                    return False
        return True

    def ejecutar_campo(self, paso, campo, segundos):
        if self.detener_evento.is_set():
            return False

        alignment_not_aligned = 1 if not self.toggle_callback() else 0
        self.callback_ui("en_proceso", paso, campo)
        id_reg = insertar_inicio(self.data, paso, campo, alignment_not_aligned)

        if self.bt:
            self.bt.enviar(segundos)

            while not self.detener_evento.is_set():
                msg = self.bt.leer()
                if msg == "DONE":
                    break
                time.sleep(0.1)
            if self.detener_evento.is_set():
                return False

        actualizar_fin(id_reg)
        self.callback_ui("terminado", paso, campo)

        # Espera de 2 segundos para ambos pasos
        for _ in range(20):
            if self.detener_evento.is_set():
                return False
            time.sleep(0.1)
        return True

    def detener(self):
        self.detener_evento.set()


# ==========================================
# 4. INTERFAZ (Tkinter)
# ==========================================
class LoginScreen:
    def __init__(self, root, on_submit, on_exit):
        self.root = root
        self.on_submit = on_submit
        self.on_exit = on_exit

        root.configure(bg=COLORS["off_white"])

        background = tk.Canvas(root, bg=COLORS["off_white"], highlightthickness=0)
        background.pack(fill="both", expand=True)
        self.login_background = background
        self.login_card_window = None
        background.bind("<Configure>", self._resize_background)

        card = ttk.Frame(background, style="Surface.TFrame", padding=(38, 28, 38, 30))
        self.login_card_window = background.create_window(0, 0, window=card, width=380)

        self.login_logos = LogoStrip(card, style="Surface.TFrame")
        self.login_logos.pack(anchor="center", pady=(0, 16))
        ttk.Label(card, text="SATMS", style="Title.TLabel").pack(pady=(0, 2))
        ttk.Label(card, text="Smart Alignment and Torque Monitoring System", style="Subtitle.TLabel").pack(pady=(0, 18))

        self.entries = {}
        campos = ["Torque ID", "User Name", "User ID", "Incubator ID"]

        for campo in campos:
            ttk.Label(card, text=campo, style="Surface.TLabel").pack(anchor="w")
            entry = ttk.Entry(card, style="Modern.TEntry")
            entry.pack(fill="x", pady=(3, 8))
            self.entries[campo] = entry

        RoundedButton(card, text="Send", command=self.submit).pack(pady=(8, 8))
        RoundedButton(card, text="Exit", command=self.on_exit).pack()

    def _resize_background(self, event):
        canvas = self.login_background
        canvas.delete("geometry")
        canvas.create_polygon(0, 0, 260, 0, 0, 210, fill=COLORS["navy"], outline="", tags="geometry")
        canvas.create_polygon(event.width, event.height, event.width - 300, event.height, event.width, event.height - 230, fill=COLORS["turquoise_light"], outline="", tags="geometry")
        canvas.create_polygon(event.width - 210, 54, event.width - 105, 105, event.width - 200, 168, fill="#D9F7FA", outline="", tags="geometry")
        canvas.tag_lower("geometry")
        if self.login_card_window:
            canvas.coords(self.login_card_window, event.width / 2, event.height / 2)

    def submit(self):
        data = (
            self.entries["Incubator ID"].get(),
            self.entries["Torque ID"].get(),
            self.entries["User ID"].get(),
            self.entries["User Name"].get(),
        )
        self.on_submit(data)


class MainScreen:
    def __init__(self, root, bluetooth, data, on_exit):
        self.root = root
        self.bt = bluetooth
        self.data = data
        self.on_exit = on_exit
        self.activo = True
        root.configure(bg=COLORS["off_white"])

        # Botón Exit en la parte superior derecha
        header = ttk.Frame(root, style="Header.TFrame", padding=(24, 18, 24, 18))
        header.pack(fill="x")

        brand = ttk.Frame(header, style="Header.TFrame")
        brand.pack(side="left")
        ttk.Label(brand, text="SATMS", style="HeaderTitle.TLabel").pack(anchor="w")
        ttk.Label(
            brand,
            text="Smart Alignment and Torque Monitoring System",
            style="HeaderDefinition.TLabel",
        ).pack(anchor="w", pady=(1, 0))
        ttk.Label(brand, text="by Ad Astra", style="HeaderCredit.TLabel").pack(anchor="w", pady=(1, 0))
        ttk.Label(
            brand,
            text=f"User: {self.data[3]}  |  Torque ID: {self.data[1]}",
            style="HeaderSubtitle.TLabel",
        ).pack(anchor="w", pady=(6, 0))

        exit_button = ttk.Button(header, text="Exit", command=self.salir, style="Exit.TButton")
        exit_button.pack(side="right")
        logo_box = ttk.Frame(header, style="HeaderLogo.TFrame", padding=(18, 10, 18, 10))
        logo_box.pack(side="right", padx=(0, 24))
        self.header_logos = LogoStrip(logo_box, style="HeaderLogo.TFrame", compact=True, max_height=57)
        self.header_logos.pack()

        # Notebook para pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=18)

        # Pestaña STEPS
        self.all_steps_frame = ttk.Frame(self.notebook, style="App.TFrame", padding=16)
        self.notebook.add(self.all_steps_frame, text="All Steps")

        self.steps_frame = ttk.Frame(self.notebook, style="App.TFrame", padding=16)
        self.notebook.add(self.steps_frame, text="Steps")

        # Pestaña RECORDS
        self.records_frame = ttk.Frame(self.notebook, style="App.TFrame", padding=16)
        self.notebook.add(self.records_frame, text="Records")

        # Configurar STEPS
        self.setup_all_steps()
        self.setup_steps()

        # Configurar RECORDS
        self.setup_records()

        # Iniciar proceso en STEPS
        self.proceso = Proceso(bluetooth, data, self.actualizar_ui, self.get_toggle_state)
        Thread(target=self.proceso.ejecutar, daemon=True).start()

    def setup_all_steps(self):
        self.all_steps_data = [
            {"title": "Step A", "instructions": [{"kind": "Action", "description": "Open eDHR, go to \"BOP_Incubators_Omni_Route\", select operation \"105: BOP_OMNI_Assy_10_5\", and enter the unit's serial number."}]},
            {"title": "Step B", "instructions": [{"kind": "Action", "description": "Connect the canopy and elevating column power box to the canopy motor, elevating column, and East rail cables."}, {"kind": "Action", "description": "Adjust canopy or column height to a comfortable position using the switch, ensuring no strange noises during movement."}]},
            {"title": "Step C", "instructions": [{"kind": "Action", "description": "Install the East upper endcap (p/n 6600-0634-700) by pulling its spring down onto the inner East rail bolt using the tool."}, {"kind": "Action", "description": "Lift the cap to verify spring retention, then record its lot number in eDHR."}]},
            {"title": "Step D", "instructions": [{"kind": "Action", "description": "Install the West upper endcap (p/n 6600-0635-700) by pulling its spring down onto the inner West rail bolt."}, {"kind": "Action", "description": "Verify spring retention, and record the lot number in eDHR."}]},
            {"title": "Step E", "instructions": [{"kind": "Action", "description": "Press the cap (p/n 6600-1150-400) into the inner East rail hole to secure it."}]},
            {"title": "Step F", "instructions": [{"kind": "Action", "description": "Assemble the East side cover (p/n 6600-1459-500) using screws on the outside and nuts on the inside, ensuring the tab is at the edge."}, {"kind": "Torque", "identifier": "2 M3 Screws (p/n 6600-0706-401) and 2 M3 Nuts (p/n 6600-0714-401).", "torque": "0.8 +/- 10% Nm."}]},
            {"title": "Step G", "instructions": [{"kind": "Action", "description": "Assemble the West side cover (p/n 6600-1477-500) using screws on the outside and nuts on the inside, ensuring the tab is at the edge."}, {"kind": "Torque", "identifier": "2 M3 Screws (p/n 6600-0706-401) and 2 M3 Nuts (p/n 6600-0714-401).", "torque": "0.8 +/- 10% Nm."}]},
            {"title": "Step H (South Wall)", "instructions": [{"kind": "Action", "description": "Loosen the two corner bracket screws on the South wall."}, {"kind": "Action", "description": "Place the alignment tool over the brackets against the wall."}, {"kind": "Torque", "identifier": "4 South wall corner bracket screws.", "torque": "1.7 +/- 10% Nm."}]},
            {"title": "Step I (North Wall)", "instructions": [{"kind": "Action", "description": "Loosen the two corner bracket screws on the North wall."}, {"kind": "Action", "description": "Place the alignment tool over the brackets against the wall."}, {"kind": "Torque", "identifier": "4 North wall corner bracket screws.", "torque": "1.7 +/- 10% Nm."}]},
            {"title": "Step J", "instructions": [{"kind": "Action", "description": "Place spacer tools onto the corner brackets."}]},
            {"title": "Step K", "instructions": [{"kind": "Action", "description": "Lower the canopy onto the spacers."}, {"kind": "Action", "description": "Lift the radiant heater bracket until it stops and hand-tighten the nuts in the specified order."}, {"kind": "Torque", "identifier": "Radiant heater bracket nuts (1, 2, 3, and 4).", "torque": "7.0 +/- 10% Nm."}]},
            {"title": "Step L", "instructions": [{"kind": "Action", "description": "Lift and lower the canopy to verify smooth, centered movement without overlapping the walls."}, {"kind": "Action", "description": "Ensure pins center in wedges and seals touch the inner walls; adjust canopy alignment if necessary."}]},
            {"title": "Step M", "instructions": [{"kind": "Action", "description": "Hand-tighten the radiant heater nuts in the specified order."}, {"kind": "Torque", "identifier": "Radiant heater nuts.", "torque": "7.0 +/- 10% Nm (in the same sequence)."}]},
            {"title": "Step N", "instructions": [{"kind": "Action", "description": "Visually verify the shipping lock is fully visible in the slot; if not, repeat the alignment."}]},
            {"title": "Canopy Verification", "instructions": [{"kind": "Action", "description": "Raise the canopy to verify heater doors open fully, then remove the 4 spacers."}, {"kind": "Action", "description": "Lower the canopy to check for flush, silent closing doors, and disconnect power box cables."}]},
            {"title": "Step P", "instructions": [{"kind": "Action", "description": "Reconnect power box cables and adjust the canopy height to a comfortable position."}]},
            {"title": "Step Q", "instructions": [{"kind": "Action", "description": "Raise canopy to ensure heater doors open fully, aluminum sheets are intact, and the reflector label is present."}, {"kind": "Action", "description": "Lower canopy to confirm silent, flush door closing; send to repair station if verification fails."}]},
            {"title": "Step R", "instructions": [{"kind": "Action", "description": "Apply final torque to the radiation heater bracket nuts and bolts."}, {"kind": "Torque", "identifier": "Radiation heater bracket nuts and bolts.", "torque": "9.15 +/- 0.67 Nm."}]},
            {"title": "Step S", "instructions": [{"kind": "Action", "description": "Place the 4 lb alignment weight on the heater bracket."}, {"kind": "Action", "description": "Fully raise and lower the canopy to verify silent door closing, centered pins, and proper seal contact, then remove the weight."}]},
            {"title": "Step T", "instructions": [{"kind": "Action", "description": "Install two buttons (p/n 6600-1788-500) on the cover (p/n 6600-1220-500) using screws, lock washers, and flat washers."}, {"kind": "Torque", "identifier": "2 M5 Screws (p/n 6600-0706-418).", "torque": "1.8 +/- 10% Nm."}]},
            {"title": "Step U", "instructions": [{"kind": "Action", "description": "Install the cover onto the canopy with 4 screws."}, {"kind": "Action", "description": "Remove the North seal, attach the soffit (p/n 6600-1461-500) with 6 clips (p/n 6600-1056-400), replace the seal, lower the canopy, and disconnect cables."}, {"kind": "Torque", "identifier": "4 M4 Screws (p/n 6600-0706-409).", "torque": "1.8 +/- 10% Nm."}]},
            {"title": "Step V", "instructions": [{"kind": "Action", "description": "Attach two giraffe labels (p/n 2082164-001) to both ends of the canopy cover using the alignment tool."}]},
            {"title": "Step W", "instructions": [{"kind": "Action", "description": "Inspect the unit for cosmetic damage; complete the DCP in eDHR if none, or reject to repair if damaged."}]},
        ]
        self.all_steps_current_step = 0
        self.all_steps_current_instruction = 0
        self.all_steps_completed = set()
        self.all_steps_expanded_steps = set()
        self.all_steps_expanded_instructions = set()
        self.all_steps_active_card = None
        self.all_steps_click_after = None

        title_row = ttk.Frame(self.all_steps_frame, style="App.TFrame")
        title_row.pack(fill="x", pady=(0, 14))
        ttk.Label(title_row, text="All Steps", style="TabTitle.TLabel").pack(side="left")

        layout = ttk.Frame(self.all_steps_frame, style="App.TFrame")
        layout.pack(fill="both", expand=True)
        layout.grid_rowconfigure(0, weight=1)
        layout.grid_columnconfigure(0, weight=1)

        list_shell = ttk.Frame(layout, style="App.TFrame")
        list_shell.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        list_shell.grid_rowconfigure(0, weight=1)
        list_shell.grid_columnconfigure(0, weight=1)

        self.all_steps_canvas = tk.Canvas(list_shell, bg=COLORS["off_white"], highlightthickness=0)
        self.all_steps_canvas.grid(row=0, column=0, sticky="nsew")
        scroll_y = ttk.Scrollbar(list_shell, orient="vertical", command=self.all_steps_canvas.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.all_steps_canvas.configure(yscrollcommand=scroll_y.set)

        self.all_steps_list = ttk.Frame(self.all_steps_canvas, style="App.TFrame")
        self.all_steps_window = self.all_steps_canvas.create_window((0, 0), window=self.all_steps_list, anchor="nw")
        self.all_steps_list.bind(
            "<Configure>",
            lambda _event: self.all_steps_canvas.configure(scrollregion=self.all_steps_canvas.bbox("all")),
        )
        self.all_steps_canvas.bind(
            "<Configure>",
            lambda event: self.all_steps_canvas.itemconfigure(self.all_steps_window, width=event.width),
        )

        controls = ttk.Frame(layout, style="Surface.TFrame", padding=(18, 18, 18, 18))
        controls.grid(row=0, column=1, sticky="ns")
        ttk.Button(
            controls,
            text="Start Simulation",
            command=lambda: self.notebook.select(self.steps_frame),
            style="Accent.TButton",
        ).pack(fill="x", pady=(0, 12))
        ttk.Button(
            controls,
            text="Siguiente v",
            command=self.advance_all_steps,
            style="Accent.TButton",
        ).pack(fill="x")

        self.render_all_steps()

    def get_all_step_status(self, step_index):
        instruction_count = len(self.all_steps_data[step_index]["instructions"])
        if all((step_index, i) in self.all_steps_completed for i in range(instruction_count)):
            return "Completed"
        if step_index == self.all_steps_current_step:
            return "In Progress"
        return "Not Completed"

    def get_all_instruction_status(self, step_index, instruction_index):
        if (step_index, instruction_index) in self.all_steps_completed:
            return "Completed"
        if (
            step_index == self.all_steps_current_step
            and instruction_index == self.all_steps_current_instruction
        ):
            return "In Progress"
        return "Not Completed"

    def schedule_all_steps_action(self, callback, *args):
        if self.all_steps_click_after:
            self.root.after_cancel(self.all_steps_click_after)
        self.all_steps_click_after = self.root.after(180, lambda: self._run_all_steps_action(callback, *args))

    def _run_all_steps_action(self, callback, *args):
        self.all_steps_click_after = None
        callback(*args)

    def cancel_all_steps_scheduled_action(self):
        if self.all_steps_click_after:
            self.root.after_cancel(self.all_steps_click_after)
            self.all_steps_click_after = None

    def expand_all_step(self, step_index):
        self.all_steps_expanded_steps.add(step_index)
        self.render_all_steps()

    def collapse_all_step(self, step_index):
        self.cancel_all_steps_scheduled_action()
        if step_index == self.all_steps_current_step:
            return
        self.all_steps_expanded_steps.discard(step_index)
        self.all_steps_expanded_instructions = {
            key for key in self.all_steps_expanded_instructions if key[0] != step_index
        }
        self.render_all_steps()

    def expand_all_instruction(self, step_index, instruction_index):
        self.all_steps_expanded_steps.add(step_index)
        self.all_steps_expanded_instructions.add((step_index, instruction_index))
        self.render_all_steps()

    def collapse_all_instruction(self, step_index, instruction_index):
        self.cancel_all_steps_scheduled_action()
        if (
            step_index == self.all_steps_current_step
            and instruction_index == self.all_steps_current_instruction
        ):
            return
        self.all_steps_expanded_instructions.discard((step_index, instruction_index))
        self.render_all_steps()

    def render_all_steps(self, keep_current_visible=False):
        for child in self.all_steps_list.winfo_children():
            child.destroy()
        self.all_steps_active_card = None

        for step_index, step in enumerate(self.all_steps_data):
            step_status = self.get_all_step_status(step_index)
            step_is_expanded = (
                step_status == "In Progress" or step_index in self.all_steps_expanded_steps
            )
            status_bg = {
                "Completed": COLORS["green"],
                "In Progress": COLORS["turquoise"],
                "Not Completed": COLORS["pending"],
            }[step_status]
            status_fg = COLORS["white"] if step_status == "In Progress" else COLORS["navy"]

            step_card = tk.Frame(
                self.all_steps_list,
                bg=COLORS["white"],
                highlightbackground=COLORS["line"],
                highlightthickness=1,
            )
            step_card.pack(fill="x", pady=(0, 10))
            if step_index == self.all_steps_current_step:
                self.all_steps_active_card = step_card

            header = tk.Frame(step_card, bg=COLORS["white"])
            header.pack(fill="x")
            step_title = tk.Label(
                header,
                text=f"{step_index + 1}. {step['title']}",
                bg=COLORS["white"],
                fg=COLORS["navy"],
                font=modern_font(13, "bold"),
                anchor="w",
                padx=16,
                pady=12,
                cursor="hand2",
            )
            step_title.pack(side="left", fill="x", expand=True)
            step_title.bind(
                "<Button-1>",
                lambda _event, i=step_index: self.schedule_all_steps_action(self.expand_all_step, i),
            )
            step_title.bind("<Double-Button-1>", lambda _event, i=step_index: self.collapse_all_step(i))

            step_badge = tk.Label(
                header,
                text=step_status,
                bg=status_bg,
                fg=status_fg,
                font=modern_font(9, "bold"),
                padx=12,
                pady=6,
                cursor="hand2",
            )
            step_badge.pack(side="right", padx=14)
            step_badge.bind(
                "<Button-1>",
                lambda _event, i=step_index: self.schedule_all_steps_action(self.expand_all_step, i),
            )
            step_badge.bind("<Double-Button-1>", lambda _event, i=step_index: self.collapse_all_step(i))

            if not step_is_expanded:
                continue

            instruction_area = tk.Frame(step_card, bg=COLORS["white"])
            instruction_area.pack(fill="x", padx=16, pady=(0, 14))
            for instruction_index, instruction in enumerate(step["instructions"]):
                instruction_status = self.get_all_instruction_status(step_index, instruction_index)
                instruction_is_expanded = (
                    instruction_status == "In Progress"
                    or (step_index, instruction_index) in self.all_steps_expanded_instructions
                )
                instruction_bg = {
                    "Completed": COLORS["green"],
                    "In Progress": COLORS["turquoise_light"],
                    "Not Completed": COLORS["pending"],
                }[instruction_status]

                instruction_card = tk.Frame(instruction_area, bg=instruction_bg)
                instruction_card.pack(fill="x", pady=4)
                instruction_header = tk.Label(
                    instruction_card,
                    text=f"{step_index + 1}.{instruction_index + 1} {instruction['kind']} - {instruction_status}",
                    bg=instruction_bg,
                    fg=COLORS["navy"],
                    font=modern_font(10, "bold"),
                    anchor="w",
                    padx=12,
                    pady=8,
                    cursor="hand2",
                )
                instruction_header.pack(fill="x")
                instruction_header.bind(
                    "<Button-1>",
                    lambda _event, s=step_index, i=instruction_index: self.schedule_all_steps_action(
                        self.expand_all_instruction, s, i
                    ),
                )
                instruction_header.bind(
                    "<Double-Button-1>",
                    lambda _event, s=step_index, i=instruction_index: self.collapse_all_instruction(s, i),
                )

                if not instruction_is_expanded:
                    continue

                if instruction["kind"] == "Torque":
                    detail = f"Identifier: {instruction['identifier']}\nTorque: {instruction['torque']}"
                else:
                    detail = instruction["description"]
                tk.Label(
                    instruction_card,
                    text=detail,
                    bg=COLORS["white"],
                    fg=COLORS["navy_2"],
                    font=modern_font(9),
                    justify="left",
                    anchor="w",
                    padx=12,
                    pady=10,
                    wraplength=760,
                ).pack(fill="x", padx=8, pady=(0, 8))

        if keep_current_visible:
            self.all_steps_canvas.after_idle(self.scroll_all_steps_to_current)

    def scroll_all_steps_to_current(self):
        if not self.all_steps_active_card:
            return
        self.all_steps_canvas.update_idletasks()
        scroll_region = self.all_steps_canvas.bbox("all")
        if not scroll_region:
            return
        content_height = max(1, scroll_region[3] - scroll_region[1])
        viewport_height = self.all_steps_canvas.winfo_height()
        target_y = max(0, self.all_steps_active_card.winfo_y() - 18)
        if content_height > viewport_height:
            self.all_steps_canvas.yview_moveto(target_y / content_height)

    def advance_all_steps(self):
        self.cancel_all_steps_scheduled_action()
        current_key = (self.all_steps_current_step, self.all_steps_current_instruction)
        self.all_steps_completed.add(current_key)
        self.all_steps_expanded_instructions.discard(current_key)

        current_step = self.all_steps_data[self.all_steps_current_step]
        if self.all_steps_current_instruction + 1 < len(current_step["instructions"]):
            self.all_steps_current_instruction += 1
        elif self.all_steps_current_step + 1 < len(self.all_steps_data):
            self.all_steps_expanded_steps.discard(self.all_steps_current_step)
            self.all_steps_current_step += 1
            self.all_steps_current_instruction = 0
        self.render_all_steps(keep_current_visible=True)

    def setup_steps(self):
        title_row = ttk.Frame(self.steps_frame, style="App.TFrame")
        title_row.pack(fill="x", pady=(0, 14))
        ttk.Label(title_row, text="SATMS Process", style="TabTitle.TLabel").pack(side="left")

        content = ttk.Frame(self.steps_frame, style="App.TFrame")
        content.pack(fill="both", expand=True)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1, uniform="steps")
        content.grid_columnconfigure(1, weight=2, uniform="steps")

        step1_frame = self._build_panel(content, "Step 1", 0, 0, (0, 10))
        self.step1_labels = {}
        for campo in range(1, 4):
            label = self._instruction_label(step1_frame, f"Instruction {campo}: Pending")
            label.pack(fill="x", pady=5)
            self.step1_labels[campo] = label

        grouped_panel = tk.Frame(content, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        grouped_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        grouped_panel.grid_columnconfigure((0, 1), weight=1, uniform="alignment_step")
        grouped_panel.grid_rowconfigure(1, weight=1)

        grouped_header = tk.Canvas(grouped_panel, height=52, bg=COLORS["white"], highlightthickness=0)
        grouped_header.grid(row=0, column=0, columnspan=2, sticky="ew")
        grouped_header.create_rectangle(0, 0, 8, 52, fill=COLORS["turquoise"], outline="")
        grouped_header.create_polygon(610, 0, 720, 0, 720, 52, fill=COLORS["turquoise_light"], outline="")
        ttk.Label(grouped_header, text="Alignment and Step 2", style="Surface.TLabel", font=modern_font(13, "bold")).place(x=24, y=15)

        alignment_frame = ttk.Frame(grouped_panel, style="Surface.TFrame", padding=(22, 12, 12, 20))
        alignment_frame.grid(row=1, column=0, sticky="nsew")
        ttk.Label(alignment_frame, text="Alignment Status", style="Surface.TLabel", font=modern_font(12, "bold")).pack(anchor="w", pady=(0, 12))
        self.alignment_label = tk.Label(
            alignment_frame,
            text="Not aligned",
            bg=COLORS["red"],
            fg=COLORS["white"],
            activebackground=COLORS["red"],
            activeforeground=COLORS["white"],
            font=modern_font(15, "bold"),
            height=2,
            relief="flat",
        )
        self.alignment_label.pack(fill="x", pady=(5, 12), ipady=8)

        self.toggle_var = tk.BooleanVar()
        self.toggle = ttk.Checkbutton(
            alignment_frame,
            text="Alignment ON/OFF",
            variable=self.toggle_var,
            command=self.toggle_changed,
            style="Modern.TCheckbutton",
        )
        self.toggle.pack(anchor="w", pady=8)

        step2_frame = ttk.Frame(grouped_panel, style="Surface.TFrame", padding=(12, 12, 22, 20))
        step2_frame.grid(row=1, column=1, sticky="nsew")
        ttk.Label(step2_frame, text="Step 2", style="Surface.TLabel", font=modern_font(12, "bold")).pack(anchor="w", pady=(0, 12))
        self.labels = {}
        for campo in range(1, 4):
            label = self._instruction_label(step2_frame, f"Instruction {campo}: Pending")
            label.pack(fill="x", pady=5)
            self.labels[(2, campo)] = label

        self.estado_label = tk.Label(
            self.steps_frame,
            text="Status: waiting to start",
            font=modern_font(11, "bold"),
            fg=COLORS["white"],
            bg=COLORS["navy_2"],
            anchor="w",
            padx=16,
            pady=10,
        )
        self.estado_label.pack(fill="x", pady=(16, 0))

    def _build_panel(self, parent, title, row, column, padx):
        panel = tk.Frame(parent, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        panel.grid(row=row, column=column, sticky="nsew", padx=padx)

        accent = tk.Canvas(panel, height=52, bg=COLORS["white"], highlightthickness=0)
        accent.pack(fill="x")
        accent.create_rectangle(0, 0, 8, 52, fill=COLORS["turquoise"], outline="")
        accent.create_polygon(285, 0, 360, 0, 360, 52, fill=COLORS["turquoise_light"], outline="")
        accent.create_polygon(0, 52, 60, 52, 0, 18, fill="#F0FBFC", outline="")
        ttk.Label(accent, text=title, style="Surface.TLabel", font=modern_font(13, "bold")).place(x=24, y=15)

        body = ttk.Frame(panel, style="Surface.TFrame", padding=(22, 6, 22, 20))
        body.pack(fill="both", expand=True)
        return body

    def _instruction_label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            bg=COLORS["pending"],
            fg=COLORS["muted"],
            font=modern_font(10, "bold"),
            anchor="w",
            padx=14,
            pady=10,
            relief="flat",
        )

    def setup_records(self):
        self.table_configs = {
            "Torque Wrench Records": {
                "columns": (
                    "id",
                    "id_incubadora",
                    "id_torquimetro",
                    "id_usuario",
                    "nombre_usuario",
                    "id_paso",
                    "id_campo",
                    "start_date",
                    "start_time",
                    "end_date",
                    "end_time",
                ),
                "headers": {
                    "id": "ID",
                    "id_incubadora": "Incubator ID",
                    "id_torquimetro": "Torque ID",
                    "id_usuario": "User ID",
                    "nombre_usuario": "User Name",
                    "id_paso": "Step",
                    "id_campo": "Instruction",
                    "start_date": "Start Date",
                    "start_time": "Start Time",
                    "end_date": "End Date",
                    "end_time": "End Time",
                },
                "widths": {
                    "id": 70,
                    "id_incubadora": 120,
                    "id_torquimetro": 110,
                    "id_usuario": 100,
                    "nombre_usuario": 135,
                    "id_paso": 80,
                    "id_campo": 105,
                    "start_date": 115,
                    "start_time": 115,
                    "end_date": 115,
                    "end_time": 115,
                },
            },
            "Alignment Status": {
                "columns": (
                    "id",
                    "id_incubadora",
                    "id_usuario",
                    "nombre_usuario",
                    "error_x",
                    "error_y",
                    "error_z",
                    "alignment",
                    "date",
                    "time",
                ),
                "headers": {
                    "id": "ID",
                    "id_incubadora": "ID Incubator",
                    "id_usuario": "ID User",
                    "nombre_usuario": "User Name",
                    "error_x": "Error in X",
                    "error_y": "Error in Y",
                    "error_z": "Error in Z",
                    "alignment": "Alignment",
                    "date": "Date",
                    "time": "Time",
                },
                "widths": {
                    "id": 70,
                    "id_incubadora": 130,
                    "id_usuario": 110,
                    "nombre_usuario": 140,
                    "error_x": 105,
                    "error_y": 105,
                    "error_z": 105,
                    "alignment": 120,
                    "date": 115,
                    "time": 115,
                },
            },
        }

        title_row = ttk.Frame(self.records_frame, style="App.TFrame")
        title_row.pack(fill="x", pady=(0, 14))
        ttk.Label(title_row, text="SATMS Records", style="TabTitle.TLabel").pack(side="left")

        controls = ttk.Frame(self.records_frame, style="Surface.TFrame", padding=(18, 14, 18, 14))
        controls.pack(fill="x", pady=(0, 14))
        controls.grid_columnconfigure(2, weight=1)

        ttk.Label(controls, text="Table view", style="Surface.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.table_view_var = tk.StringVar(value="Torque Wrench Records")
        self.table_selector = ttk.Combobox(
            controls,
            textvariable=self.table_view_var,
            values=tuple(self.table_configs.keys()),
            state="readonly",
            style="Modern.TCombobox",
            width=24,
        )
        self.table_selector.grid(row=1, column=0, sticky="ew", padx=(0, 14), pady=(5, 0))
        self.table_selector.bind("<<ComboboxSelected>>", self._table_view_changed)

        ttk.Label(controls, text="Search by", style="Surface.TLabel").grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.search_column_var = tk.StringVar()
        self.search_column_combo = ttk.Combobox(
            controls,
            textvariable=self.search_column_var,
            state="readonly",
            style="Modern.TCombobox",
            width=22,
        )
        self.search_column_combo.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=(5, 0))

        ttk.Label(controls, text="Search value", style="Surface.TLabel").grid(row=0, column=2, sticky="w")
        self.filtro_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.filtro_var, style="Modern.TEntry").grid(row=1, column=2, sticky="ew", pady=(5, 0))

        buttons = ttk.Frame(controls, style="Surface.TFrame")
        buttons.grid(row=1, column=3, sticky="e", padx=(14, 0), pady=(5, 0))
        ttk.Button(buttons, text="Filter", command=self.filtrar, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Show all", command=self.mostrar_todos, style="Ghost.TButton").pack(side="left")

        self.table_title_label = ttk.Label(self.records_frame, text="Torque Wrench Records", style="Section.TLabel")
        self.table_title_label.pack(anchor="w", pady=(0, 8))

        tabla_frame = ttk.Frame(self.records_frame, style="Surface.TFrame", padding=(1, 1, 1, 1))
        tabla_frame.pack(fill="both", expand=True)

        self.tabla = ttk.Treeview(tabla_frame, show="headings", height=12, style="Modern.Treeview")
        self.tabla.tag_configure("odd", background=COLORS["white"], foreground=COLORS["navy"])
        self.tabla.tag_configure("even", background=COLORS["turquoise_light"], foreground=COLORS["navy"])
        self.tabla.tag_configure("aligned", foreground=COLORS["green_dark"])
        self.tabla.tag_configure("not_aligned", foreground=COLORS["red_dark"])

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        self.filtro_var.trace_add("write", self._filtrar_en_vivo)
        self._table_view_changed()

    def _table_view_changed(self, _event=None):
        config = self.table_configs[self.table_view_var.get()]
        columns = config["columns"]
        headers = config["headers"]
        self.table_title_label.config(text=self.table_view_var.get())
        self.tabla.configure(columns=columns)

        for column in columns:
            self.tabla.heading(column, text=headers[column])
            self.tabla.column(column, width=config["widths"].get(column, 110), anchor="center")

        search_options = [headers[column] for column in columns]
        self.search_column_combo.configure(values=search_options)
        if self.search_column_var.get() not in search_options:
            self.search_column_var.set(search_options[0])
        self.cargar_registros(self.filtro_var.get().strip())

    def _current_search_column(self):
        config = self.table_configs[self.table_view_var.get()]
        selected_label = self.search_column_var.get()
        for column, label in config["headers"].items():
            if label == selected_label:
                return column
        return config["columns"][0]

    def _split_datetime(self, value):
        if value and " " in value:
            return value.split(" ", 1)
        return value or "", ""

    def _row_matches_filter(self, row_values, columns, search_column, query):
        if not query:
            return True
        row_map = dict(zip(columns, row_values))
        return query.lower() in str(row_map.get(search_column, "")).lower()

    def toggle_changed(self):
        if self.toggle_var.get():
            self.alignment_label.config(text="Aligned", bg=COLORS["green"])
        else:
            self.alignment_label.config(text="Not aligned", bg=COLORS["red"])

    def get_toggle_state(self):
        return self.toggle_var.get()

    def actualizar_ui(self, estado, paso, campo=None):
        if self.activo:
            self.root.after(0, self._actualizar_ui_en_hilo_principal, estado, paso, campo)

    def _actualizar_ui_en_hilo_principal(self, estado, paso, campo=None):
        if not self.activo:
            return

        if estado == "en_proceso":
            if paso == 1:
                self.step1_labels[campo].config(
                    text=f"Instruction {campo}: In progress",
                    bg=COLORS["turquoise"],
                    fg=COLORS["white"],
                )
            elif paso == 2:
                self.labels[(paso, campo)].config(
                    text=f"Instruction {campo}: In progress",
                    bg=COLORS["turquoise"],
                    fg=COLORS["white"],
                )
            self.estado_label.config(text=f"Status: Step {paso}, instruction {campo} in progress")
        elif estado == "terminado":
            if paso == 1:
                self.step1_labels[campo].config(
                    text=f"✓ Instruction {campo}: Completed",
                    bg=COLORS["green"],
                    fg=COLORS["navy"],
                )
            elif paso == 2:
                self.labels[(paso, campo)].config(
                    text=f"✓ Instruction {campo}: Completed",
                    bg=COLORS["green"],
                    fg=COLORS["navy"],
                )
            self.estado_label.config(text=f"Status: Step {paso}, instruction {campo} completed")
        elif estado == "proceso_finalizado":
            self.estado_label.config(text="Station 10.5 completed")

    def cargar_registros(self, filtro=None):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        current_view = self.table_view_var.get()
        config = self.table_configs[current_view]
        columns = config["columns"]
        search_column = self._current_search_column()
        query = filtro or ""
        rendered_index = 0

        for registro in obtener_registros():
            (
                id_reg,
                id_inc,
                id_torq,
                id_usu,
                nom_usu,
                id_paso,
                id_campo,
                alignment_not_aligned,
                fecha_inicio,
                fecha_fin,
            ) = registro

            start_date, start_time = self._split_datetime(fecha_inicio)
            end_date, end_time = self._split_datetime(fecha_fin)

            if current_view == "Torque Wrench Records":
                row_values = (
                    id_reg,
                    id_inc,
                    id_torq,
                    id_usu,
                    nom_usu,
                    id_paso,
                    id_campo,
                    start_date,
                    start_time,
                    end_date,
                    end_time,
                )
                row_tags = ["even" if rendered_index % 2 else "odd"]
            else:
                alignment_text = "Not aligned" if alignment_not_aligned else "Aligned"
                row_values = (
                    id_reg,
                    id_inc,
                    id_usu,
                    nom_usu,
                    "",
                    "",
                    "",
                    alignment_text,
                    start_date,
                    start_time,
                )
                row_tags = ["even" if rendered_index % 2 else "odd"]
                row_tags.append("not_aligned" if alignment_not_aligned else "aligned")

            if not self._row_matches_filter(row_values, columns, search_column, query):
                continue

            self.tabla.insert("", "end", values=row_values, tags=tuple(row_tags))
            rendered_index += 1

    def filtrar(self):
        self.cargar_registros(self.filtro_var.get().strip())

    def mostrar_todos(self):
        self.filtro_var.set("")
        self.cargar_registros()

    def _filtrar_en_vivo(self, *_args):
        self.cargar_registros(self.filtro_var.get().strip())

    def salir(self):
        self.detener()
        self.on_exit()

    def detener(self):
        self.activo = False
        if self.proceso:
            self.proceso.detener()


# ==========================================
# 5. MAIN
# ==========================================
current_screen = None


def limpiar_pantalla():
    global current_screen
    if current_screen and hasattr(current_screen, "detener"):
        current_screen.detener()
    for widget in root.winfo_children():
        widget.destroy()
    current_screen = None


def mostrar_inicio():
    global current_screen
    limpiar_pantalla()
    root.geometry("1200x650")
    root.minsize(980, 620)
    current_screen = LoginScreen(root, iniciar_proceso, mostrar_inicio)


def iniciar_proceso(data):
    global current_screen
    limpiar_pantalla()
    root.geometry("1200x650")  # Ajustar tamano para pestanas
    root.minsize(980, 620)
    current_screen = MainScreen(root, bt, data, mostrar_inicio)


def mostrar_registros():
    # Ya no se usa, los registros están en la pestaña
    pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("SATMS")
    configure_global_style(root)

    init_db()

    try:
        bt = Bluetooth("COM6")
    except Exception as e:
        print(f"Warning: Could not connect to COM7 port ({e}).")
        print("The system will continue without sending Bluetooth commands for interface testing.")
        bt = None

    mostrar_inicio()
    root.mainloop()
