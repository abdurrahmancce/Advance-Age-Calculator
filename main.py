"""
╔══════════════════════════════════════════════════════════════╗
║           🎂  Age Calculator - GUI Version (Tkinter)  🎂    ║
╚══════════════════════════════════════════════════════════════╝
Run: python age_calculator_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, date
import os


# ──────────────────────────────────────────────
#  CONSTANTS & CONFIG
# ──────────────────────────────────────────────
HISTORY_FILE = "age_history.txt"

COLORS = {
    "bg":          "#0F172A",   # deep navy
    "card":        "#1E293B",   # card surface
    "card2":       "#273549",   # slightly lighter card
    "accent":      "#6366F1",   # indigo
    "accent2":     "#8B5CF6",   # violet
    "success":     "#10B981",   # emerald
    "warning":     "#F59E0B",   # amber
    "danger":      "#EF4444",   # red
    "text":        "#F1F5F9",   # near-white
    "subtext":     "#94A3B8",   # slate
    "border":      "#334155",   # border
    "highlight":   "#312E81",   # deep indigo highlight
}

FONTS = {
    "title":   ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 13, "bold"),
    "body":    ("Segoe UI", 11),
    "small":   ("Segoe UI", 9),
    "mono":    ("Consolas", 11),
    "stat":    ("Segoe UI", 20, "bold"),
    "label":   ("Segoe UI", 10),
}

ZODIAC_SIGNS = [
    ((1, 20),  (2, 18),  "Aquarius",     "♒"),
    ((2, 19),  (3, 20),  "Pisces",       "♓"),
    ((3, 21),  (4, 19),  "Aries",        "♈"),
    ((4, 20),  (5, 20),  "Taurus",       "♉"),
    ((5, 21),  (6, 20),  "Gemini",       "♊"),
    ((6, 21),  (7, 22),  "Cancer",       "♋"),
    ((7, 23),  (8, 22),  "Leo",          "♌"),
    ((8, 23),  (9, 22),  "Virgo",        "♍"),
    ((9, 23),  (10, 22), "Libra",        "♎"),
    ((10, 23), (11, 21), "Scorpio",      "♏"),
    ((11, 22), (12, 21), "Sagittarius",  "♐"),
    ((12, 22), (1, 19),  "Capricorn",    "♑"),
]


# ──────────────────────────────────────────────
#  CALCULATION LOGIC (same as CLI version)
# ──────────────────────────────────────────────

def calculate_age_years(dob: date, today: date) -> int:
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years

def calculate_total_months(dob: date, today: date) -> int:
    months = (today.year - dob.year) * 12 + (today.month - dob.month)
    if today.day < dob.day:
        months -= 1
    return months

def calculate_total_days(dob: date, today: date) -> int:
    return (today - dob).days

def days_until_next_birthday(dob: date, today: date):
    year = today.year
    try:
        next_bday = dob.replace(year=year)
    except ValueError:
        next_bday = date(year, 3, 1)
    if next_bday <= today:
        year += 1
        try:
            next_bday = dob.replace(year=year)
        except ValueError:
            next_bday = date(year, 3, 1)
    return (next_bday - today).days, next_bday

def get_zodiac_sign(dob: date):
    m, d = dob.month, dob.day
    for (sm, sd), (em, ed), name, symbol in ZODIAC_SIGNS:
        if sm > em:
            if (m == sm and d >= sd) or (m == em and d <= ed):
                return name, symbol
        else:
            if (m == sm and d >= sd) or (m > sm and m < em) or (m == em and d <= ed):
                return name, symbol
    return "Unknown", "?"


# ──────────────────────────────────────────────
#  GUI APPLICATION
# ──────────────────────────────────────────────

class AgeCalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_root()
        self._build_ui()
        self._start_clock()

    # ── Window Setup ─────────────────────────────────────────

    def _configure_root(self):
        self.root.title("🎂 Age Calculator")
        self.root.geometry("780x720")
        self.root.minsize(700, 640)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 780) // 2
        y = (self.root.winfo_screenheight() - 720) // 2
        self.root.geometry(f"+{x}+{y}")

    # ── UI Construction ───────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg=COLORS["accent"], pady=14)
        header.pack(fill="x")

        tk.Label(header, text="🎂  Age Calculator",
                 font=FONTS["title"], bg=COLORS["accent"],
                 fg=COLORS["text"]).pack()

        self.clock_var = tk.StringVar()
        tk.Label(header, textvariable=self.clock_var,
                 font=FONTS["small"], bg=COLORS["accent"],
                 fg="#C7D2FE").pack(pady=(2, 0))

        # ── Notebook (tabs) ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",
                        background=COLORS["bg"],
                        borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=COLORS["card"],
                        foreground=COLORS["subtext"],
                        padding=[14, 6],
                        font=FONTS["body"])
        style.map("TNotebook.Tab",
                  background=[("selected", COLORS["accent"])],
                  foreground=[("selected", COLORS["text"])])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_calc    = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.tab_history = tk.Frame(self.notebook, bg=COLORS["bg"])

        self.notebook.add(self.tab_calc,    text="  📅  Calculator  ")
        self.notebook.add(self.tab_history, text="  📁  History  ")

        self._build_calculator_tab()
        self._build_history_tab()

    # ── Calculator Tab ────────────────────────────────────────

    def _build_calculator_tab(self):
        parent = self.tab_calc

        # ── Input card ──
        input_card = tk.Frame(parent, bg=COLORS["card"],
                              relief="flat", bd=0)
        input_card.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(input_card, text="  Enter Your Date of Birth",
                 font=FONTS["heading"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", padx=12, pady=(12, 4))

        # ── Three separate fields: Day / Month / Year ──
        fields_row = tk.Frame(input_card, bg=COLORS["card"])
        fields_row.pack(fill="x", padx=12, pady=(6, 4))

        def make_field(parent, label_text, width, max_val):
            col = tk.Frame(parent, bg=COLORS["card"])
            col.pack(side="left", padx=(0, 10))
            tk.Label(col, text=label_text,
                     font=FONTS["small"], bg=COLORS["card"],
                     fg=COLORS["subtext"]).pack(anchor="w")
            var = tk.StringVar()
            entry = tk.Entry(
                col, textvariable=var,
                font=("Consolas", 15, "bold"),
                bg=COLORS["card2"], fg=COLORS["text"],
                insertbackground=COLORS["accent"],
                relief="flat", width=width, bd=8,
                justify="center"
            )
            entry.pack(ipady=7)
            return var, entry

        self.day_var,   self.day_entry   = make_field(fields_row, "Day (1–31)",    4,  31)
        self.month_var, self.month_entry = make_field(fields_row, "Month (1–12)",  4,  12)
        self.year_var,  self.year_entry  = make_field(fields_row, "Year (≥ 1900)", 6, 9999)

        # Tab/Enter auto-advance between fields
        self.day_entry.bind("<Return>",   lambda e: self.month_entry.focus())
        self.month_entry.bind("<Return>", lambda e: self.year_entry.focus())
        self.year_entry.bind("<Return>",  lambda e: self._calculate())

        # Numeric-only validation
        vcmd = (self.root.register(lambda s: s.isdigit() or s == ""), "%P")
        for entry in (self.day_entry, self.month_entry, self.year_entry):
            entry.config(validate="key", validatecommand=vcmd)

        # Buttons row
        btn_row = tk.Frame(input_card, bg=COLORS["card"])
        btn_row.pack(fill="x", padx=12, pady=(4, 4))

        calc_btn = tk.Button(
            btn_row,
            text="  Calculate  🔍",
            font=FONTS["heading"],
            bg=COLORS["accent"],
            fg="white",
            activebackground=COLORS["accent2"],
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=16, pady=8,
            command=self._calculate
        )
        calc_btn.pack(side="left")

        clear_btn = tk.Button(
            btn_row,
            text=" Clear ",
            font=FONTS["body"],
            bg=COLORS["card2"],
            fg=COLORS["subtext"],
            activebackground=COLORS["border"],
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=10, pady=8,
            command=self._clear
        )
        clear_btn.pack(side="left", padx=(8, 0))

        self.error_label = tk.Label(
            input_card, text="",
            font=FONTS["small"], bg=COLORS["card"],
            fg=COLORS["danger"]
        )
        self.error_label.pack(anchor="w", padx=12, pady=(2, 8))

        # ── Stats grid ──
        self.stats_frame = tk.Frame(parent, bg=COLORS["bg"])
        self.stats_frame.pack(fill="x", padx=16, pady=4)

        self.stat_vars = {}
        stat_defs = [
            ("age_years",  "🎂", "Age",       COLORS["accent"]),
            ("months",     "📅", "Months",    COLORS["success"]),
            ("days",       "📆", "Days",      COLORS["warning"]),
            ("countdown",  "⏳", "Countdown", COLORS["danger"]),
        ]
        for col, (key, icon, label, color) in enumerate(stat_defs):
            card = tk.Frame(self.stats_frame, bg=COLORS["card"],
                            relief="flat", bd=0)
            card.grid(row=0, column=col, padx=5, pady=4, sticky="nsew")
            self.stats_frame.columnconfigure(col, weight=1)

            tk.Label(card, text=icon, font=("Segoe UI Emoji", 18),
                     bg=COLORS["card"], fg=color).pack(pady=(10, 0))

            var = tk.StringVar(value="—")
            self.stat_vars[key] = var
            tk.Label(card, textvariable=var,
                     font=FONTS["stat"], bg=COLORS["card"],
                     fg=color).pack()

            tk.Label(card, text=label,
                     font=FONTS["small"], bg=COLORS["card"],
                     fg=COLORS["subtext"]).pack(pady=(0, 10))

        # ── Detail card ──
        self.detail_frame = tk.Frame(parent, bg=COLORS["card"])
        self.detail_frame.pack(fill="both", expand=True,
                               padx=16, pady=(4, 12))

        tk.Label(self.detail_frame, text="  📊  Detailed Breakdown",
                 font=FONTS["heading"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", padx=12, pady=(12, 6))

        self.detail_text = tk.Text(
            self.detail_frame,
            font=FONTS["mono"],
            bg=COLORS["card2"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            bd=8,
            state="disabled",
            height=9,
            cursor="arrow"
        )
        self.detail_text.pack(fill="both", expand=True,
                               padx=12, pady=(0, 12))

        # Tag colours for rich text
        self.detail_text.tag_configure("label",   foreground=COLORS["subtext"])
        self.detail_text.tag_configure("value",   foreground=COLORS["text"])
        self.detail_text.tag_configure("accent",  foreground=COLORS["accent"])
        self.detail_text.tag_configure("success", foreground=COLORS["success"])
        self.detail_text.tag_configure("warning", foreground=COLORS["warning"])
        self.detail_text.tag_configure("birthday",foreground=COLORS["warning"],
                                        font=("Segoe UI", 12, "bold"))

    # ── History Tab ───────────────────────────────────────────

    def _build_history_tab(self):
        parent = self.tab_history

        btn_row = tk.Frame(parent, bg=COLORS["bg"])
        btn_row.pack(fill="x", padx=16, pady=(14, 6))

        tk.Label(btn_row, text="📁  Saved Calculations",
                 font=FONTS["heading"], bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(side="left")

        tk.Button(btn_row, text="🔄 Refresh",
                  font=FONTS["body"], bg=COLORS["accent"],
                  fg="white", relief="flat", cursor="hand2",
                  padx=10, pady=4,
                  command=self._load_history).pack(side="right")

        tk.Button(btn_row, text="🗑 Clear History",
                  font=FONTS["body"], bg=COLORS["danger"],
                  fg="white", relief="flat", cursor="hand2",
                  padx=10, pady=4,
                  command=self._clear_history).pack(side="right", padx=(0, 8))

        self.history_text = scrolledtext.ScrolledText(
            parent,
            font=FONTS["mono"],
            bg=COLORS["card"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            bd=8,
            state="disabled",
            cursor="arrow"
        )
        self.history_text.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        self._load_history()

    # ── Clock ─────────────────────────────────────────────────

    def _start_clock(self):
        def tick():
            now = datetime.now()
            self.clock_var.set(
                now.strftime("  📅  %A, %d %B %Y     🕐  %I:%M:%S %p  ")
            )
            self.root.after(1000, tick)
        tick()

    # ── Event Handlers ────────────────────────────────────────

    def _calculate(self):
        self.error_label.config(text="")

        day_s   = self.day_var.get().strip()
        month_s = self.month_var.get().strip()
        year_s  = self.year_var.get().strip()

        if not day_s:
            self.error_label.config(text="⚠  Please enter the Day.")
            self.day_entry.focus(); return
        if not month_s:
            self.error_label.config(text="⚠  Please enter the Month.")
            self.month_entry.focus(); return
        if not year_s:
            self.error_label.config(text="⚠  Please enter the Year.")
            self.year_entry.focus(); return

        try:
            d, m, y = int(day_s), int(month_s), int(year_s)
            dob = date(y, m, d)
        except ValueError:
            self.error_label.config(
                text=f"⚠  {day_s}/{month_s}/{year_s} is not a valid date."
            )
            self.day_entry.focus()
            return

        today = date.today()
        if dob > today:
            self.error_label.config(text="⚠  Date of birth cannot be in the future.")
            return
        if dob.year < 1900:
            self.error_label.config(text="⚠  Year must be 1900 or later.")
            return

        # ── Computations ──
        age_years  = calculate_age_years(dob, today)
        age_months = calculate_total_months(dob, today)
        age_days   = calculate_total_days(dob, today)
        days_left, next_bday = days_until_next_birthday(dob, today)
        zodiac_name, zodiac_sym = get_zodiac_sign(dob)
        is_birthday = (today.month == dob.month and today.day == dob.day)

        # ── Update stat cards ──
        self.stat_vars["age_years"].set(f"{age_years}")
        self.stat_vars["months"].set(f"{age_months:,}")
        self.stat_vars["days"].set(f"{age_days:,}")
        self.stat_vars["countdown"].set(
            "TODAY! 🎉" if is_birthday else f"{days_left}d"
        )

        # ── Detail text ──
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")

        def row(label, value, tag="value"):
            self.detail_text.insert("end", f"  {label:<26}", "label")
            self.detail_text.insert("end", f"{value}\n", tag)

        if is_birthday:
            self.detail_text.insert("end",
                "  🎉🎊  HAPPY BIRTHDAY! 🎊🎉\n\n", "birthday")

        row("Date of Birth :",
            dob.strftime("%d %B %Y (%A)"))
        row("Calculated On :",
            datetime.now().strftime("%d %B %Y, %I:%M %p"))
        self.detail_text.insert("end", "\n")
        row("Age in Years :",   f"{age_years} years", "accent")
        row("Total Months :",   f"{age_months:,} months", "accent")
        row("Total Days :",     f"{age_days:,} days", "accent")
        row("Total Hours :",    f"{age_days * 24:,} hours")
        row("Total Minutes :",  f"{age_days * 24 * 60:,} minutes")
        self.detail_text.insert("end", "\n")
        row("Next Birthday :",
            f"{next_bday.strftime('%d %B %Y')}  ({days_left} days away)",
            "success")
        row("Zodiac Sign :",
            f"{zodiac_sym} {zodiac_name}", "warning")

        self.detail_text.config(state="disabled")

        # ── Save to history ──
        self._save_to_history(dob, age_years, age_days, zodiac_name)
        self._load_history()

    def _clear(self):
        self.day_var.set("")
        self.month_var.set("")
        self.year_var.set("")
        self.error_label.config(text="")
        for v in self.stat_vars.values():
            v.set("—")
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.config(state="disabled")
        self.day_entry.focus()

    # ── History Helpers ───────────────────────────────────────

    def _save_to_history(self, dob: date, age: int, days: int, zodiac: str):
        record = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  "
            f"DOB: {dob.strftime('%d/%m/%Y')}  |  "
            f"Age: {age} yrs  |  Days: {days:,}  |  Zodiac: {zodiac}\n"
        )
        try:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(record)
        except OSError:
            pass  # Silently ignore write failures

    def _load_history(self):
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                self.history_text.insert("end", "  No history yet. Run a calculation first.")
            else:
                for i, line in enumerate(reversed(lines), 1):
                    self.history_text.insert("end", f"  {i:>3}.  {line}")
        except FileNotFoundError:
            self.history_text.insert("end",
                "  No history file found.\n  Run a calculation to create one.")
        self.history_text.config(state="disabled")

    def _clear_history(self):
        if messagebox.askyesno("Clear History",
                               "Are you sure you want to clear all history?"):
            try:
                os.remove(HISTORY_FILE)
            except FileNotFoundError:
                pass
            self._load_history()


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

def main():
    root = tk.Tk()
    app = AgeCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()