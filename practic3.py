"""
Трекер личных финансов — CustomTkinter
"""

import customtkinter as ctk
from datetime import datetime
import json
import os

DATA_FILE = "finance_data.json"


# ─── Данные ──────────────────────────────────────────────
def _data_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)

def load_data():
    path = _data_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "transactions": [],
        "categories": [
            {"name": "Зарплата", "type": "income"},
            {"name": "Фриланс", "type": "income"},
            {"name": "Подарки", "type": "income"},
            {"name": "Еда", "type": "expense"},
            {"name": "Транспорт", "type": "expense"},
            {"name": "Развлечения", "type": "expense"},
            {"name": "Подписки", "type": "expense"},
            {"name": "Аренда", "type": "expense"},
            {"name": "Другое", "type": "expense"},
        ],
        "goals": [],
        "settings": {"currency": "KGS", "theme": "dark", "notifications": True},
    }


def save_data(data):
    path = _data_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Цвета ───────────────────────────────────────────────
DARK = {
    "bg": "#0d1a14",
    "sidebar": "#0f1f17",
    "card": "#132a1e",
    "fg": "#d4e8dc",
    "muted": "#6b8f7b",
    "green": "#2ecc71",
    "green_dark": "#1a8a4a",
    "red": "#e74c3c",
    "border": "#1e3a2a",
    "input_bg": "#1a2f22",
    "yellow": "#f1c40f",
}

LIGHT = {
    "bg": "#f5f7f6",
    "sidebar": "#e8eeea",
    "card": "#ffffff",
    "fg": "#1a2e22",
    "muted": "#6b8f7b",
    "green": "#27ae60",
    "green_dark": "#1e8449",
    "red": "#e74c3c",
    "border": "#c8d6ce",
    "input_bg": "#edf2ee",
    "yellow": "#f39c12",
}


# ─── Главное приложение ──────────────────────────────────
class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("💰 Трекер личных финансов")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.data = load_data()
        self.colors = DARK if self.data["settings"]["theme"] == "dark" else LIGHT
        self.configure(fg_color=self.colors["bg"])

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, fg_color=self.colors["sidebar"], width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self._build_sidebar()
        self.show_dashboard()

    def _build_sidebar(self):
        c = self.colors
        self.sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.sidebar, text="💰 Finance",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=c["green"],
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=c["border"]).grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.sidebar.grid_columnconfigure(0, weight=1)

        buttons = [
            ("📊  Мои финансы", self.show_dashboard),
            ("📋  Транзакции", self.show_transactions),
            ("📈  Аналитика", self.show_analytics),
            ("🏷️  Категории", self.show_categories),
            ("🎯  Цели", self.show_goals),
            ("⚙️  Настройки", self.show_settings),
            ("❓  Справка", self.show_help),
        ]

        self.nav_buttons = []
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=10)
        nav_frame.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        for i, (text, cmd) in enumerate(buttons):
            btn = ctk.CTkButton(
                nav_frame, text=text, anchor="w",
                fg_color="transparent",
                hover_color=c["border"],
                text_color=c["fg"],
                font=ctk.CTkFont(size=11),
                height=36,
                command=cmd,
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self.nav_buttons.append(btn)

        ctk.CTkButton(
            self.sidebar, text="＋ Добавить доход",
            fg_color=c["green"], hover_color=c["green_dark"],
            text_color="#0d1a14", font=ctk.CTkFont(size=10, weight="bold"),
            command=lambda: self._add_transaction_dialog("income"),
        ).grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))
        ctk.CTkButton(
            self.sidebar, text="＋ Добавить расход",
            fg_color=c["card"], hover_color=c["border"],
            text_color=c["green"], font=ctk.CTkFont(size=10),
            command=lambda: self._add_transaction_dialog("expense"),
        ).grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 15))

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _header(self, text):
        c = self.colors
        ctk.CTkLabel(
            self.content, text=text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=c["fg"],
        ).grid(row=0, column=0, sticky="w", padx=0, pady=(20, 15))

    def _card(self, parent, **kwargs):
        c = self.colors
        return ctk.CTkFrame(
            parent, fg_color=c["card"],
            corner_radius=8, border_width=1, border_color=c["border"],
            **kwargs
        )

    def _calc_balance(self):
        inc = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "income")
        exp = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "expense")
        return inc, exp, inc - exp

    # ── 1. Мои финансы ──
    def show_dashboard(self):
        self._clear_content()
        self.content.grid_rowconfigure(1, weight=1)
        self._header("Мои финансы")
        c = self.colors
        inc, exp, bal = self._calc_balance()
        cur = self.data["settings"]["currency"]

        cards_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for i, (label, value, color) in enumerate([
            ("Баланс", f"{bal:,.0f} {cur}", c["fg"]),
            ("Доходы", f"+{inc:,.0f} {cur}", c["green"]),
            ("Расходы", f"-{exp:,.0f} {cur}", c["red"]),
        ]):
            card = self._card(cards_frame)
            card.grid(row=0, column=i, padx=(0, 10), sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=10), text_color=c["muted"]).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 2))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold"), text_color=color).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 12))

        recent_card = self._card(self.content)
        recent_card.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        recent_card.grid_columnconfigure(0, weight=1)
        recent_card.grid_rowconfigure(1, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(recent_card, text="Последние операции", font=ctk.CTkFont(size=12, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 5))

        tree_frame = ctk.CTkScrollableFrame(recent_card, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        tree_frame.grid_columnconfigure(0, weight=1)

        for i, t in enumerate(self.data["transactions"][:10]):
            sign = "+" if t["type"] == "income" else "-"
            row = ctk.CTkFrame(tree_frame, fg_color="transparent")
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row, text=t["date"], text_color=c["muted"], width=100).grid(row=0, column=0, sticky="w", padx=5, pady=2)
            ctk.CTkLabel(row, text="Доход" if t["type"] == "income" else "Расход", text_color=c["fg"], width=80).grid(row=0, column=1, sticky="w", padx=5, pady=2)
            ctk.CTkLabel(row, text=t["category"], text_color=c["fg"], width=150).grid(row=0, column=2, sticky="w", padx=5, pady=2)
            ctk.CTkLabel(row, text=f"{sign}{t['amount']:,.0f} {cur}", text_color=c["green"] if t["type"] == "income" else c["red"], width=120).grid(row=0, column=3, sticky="e", padx=5, pady=2)
            row.grid(row=i, column=0, sticky="ew", pady=2)

    # ── 2. Транзакции ──
    def show_transactions(self):
        self._clear_content()
        self.content.grid_rowconfigure(2, weight=1)
        self._header("Транзакции")
        c = self.colors
        cur = self.data["settings"]["currency"]

        btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="w", pady=(0, 10))
        ctk.CTkButton(
            btn_frame, text="＋ Добавить доход",
            fg_color=c["green"], text_color="#0d1a14", font=ctk.CTkFont(size=10, weight="bold"),
            command=lambda: self._add_transaction_dialog("income"),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_frame, text="＋ Добавить расход",
            fg_color=c["card"], text_color=c["green"], font=ctk.CTkFont(size=10),
            command=lambda: self._add_transaction_dialog("expense"),
        ).pack(side="left", padx=(0, 8))

        card = self._card(self.content)
        card.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        trans_scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        trans_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        trans_scroll.grid_columnconfigure(0, weight=1)

        self.trans_items = []
        for i, t in enumerate(self.data["transactions"]):
            sign = "+" if t["type"] == "income" else "-"
            row = ctk.CTkFrame(trans_scroll, fg_color="transparent")
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row, text=t["date"], text_color=c["muted"], width=100).grid(row=0, column=0, sticky="w", padx=5, pady=4)
            ctk.CTkLabel(row, text="Доход" if t["type"] == "income" else "Расход", text_color=c["fg"], width=80).grid(row=0, column=1, sticky="w", padx=5, pady=4)
            ctk.CTkLabel(row, text=t["category"], text_color=c["fg"], width=130).grid(row=0, column=2, sticky="w", padx=5, pady=4)
            ctk.CTkLabel(row, text=f"{sign}{t['amount']:,.0f} {cur}", text_color=c["green"] if t["type"] == "income" else c["red"], width=120).grid(row=0, column=3, sticky="e", padx=5, pady=4)
            ctk.CTkLabel(row, text=t.get("comment", ""), text_color=c["muted"], width=150).grid(row=0, column=4, sticky="w", padx=5, pady=4)
            del_btn = ctk.CTkButton(row, text="🗑", width=32, fg_color="transparent", hover_color=c["red"], command=lambda idx=i: self._delete_transaction_at(idx))
            del_btn.grid(row=0, column=5, padx=5, pady=4)
            self.trans_items.append((row, t))
            row.grid(row=i, column=0, sticky="ew", pady=2)
        trans_scroll.grid_columnconfigure(0, weight=1)

        self.trans_scroll = trans_scroll
        self.trans_card = card

    def _delete_transaction_at(self, idx):
        self.data["transactions"].pop(idx)
        save_data(self.data)
        self.show_transactions()

    def _add_transaction_dialog(self, tx_type):
        c = self.colors
        win = ctk.CTkToplevel(self)
        win.title("Добавить доход" if tx_type == "income" else "Добавить расход")
        win.geometry("400x350")
        win.configure(fg_color=c["card"])
        win.resizable(False, False)

        cats = [cat["name"] for cat in self.data["categories"] if cat["type"] == tx_type]
        ctk.CTkLabel(win, text="Категория:", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(20, 2))
        cat_var = ctk.StringVar(value=cats[0] if cats else "")
        cat_menu = ctk.CTkOptionMenu(win, variable=cat_var, values=cats if cats else ["Другое"])
        cat_menu.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(win, text="Сумма:", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(0, 2))
        amount_entry = ctk.CTkEntry(win, fg_color=c["input_bg"], placeholder_text="0")
        amount_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(win, text="Дата (ГГГГ-ММ-ДД):", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(0, 2))
        date_entry = ctk.CTkEntry(win, fg_color=c["input_bg"])
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(win, text="Комментарий:", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(0, 2))
        comment_entry = ctk.CTkEntry(win, fg_color=c["input_bg"], placeholder_text="")
        comment_entry.pack(fill="x", padx=20, pady=(0, 15))

        def save():
            try:
                amt = float(amount_entry.get())
                if amt <= 0:
                    raise ValueError
            except ValueError:
                return
            self.data["transactions"].insert(0, {
                "type": tx_type,
                "category": cat_var.get(),
                "amount": amt,
                "date": date_entry.get(),
                "comment": comment_entry.get(),
            })
            save_data(self.data)
            win.destroy()
            self.show_dashboard()

        ctk.CTkButton(win, text="💾 Сохранить", fg_color=c["green"], text_color="#0d1a14", font=ctk.CTkFont(weight="bold"), command=save).pack(pady=(5, 20))

    # ── 3. Аналитика ──
    def show_analytics(self):
        self._clear_content()
        self.content.grid_rowconfigure(1, weight=1)
        self._header("Аналитика")
        c = self.colors
        cur = self.data["settings"]["currency"]

        expenses = {}
        incomes = {}
        for t in self.data["transactions"]:
            if t["type"] == "expense":
                expenses[t["category"]] = expenses.get(t["category"], 0) + t["amount"]
            else:
                incomes[t["category"]] = incomes.get(t["category"], 0) + t["amount"]

        card = self._card(self.content)
        card.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="Расходы по категориям", font=ctk.CTkFont(size=13, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 10))

        if expenses:
            total_exp = sum(expenses.values())
            for i, (cat, amt) in enumerate(sorted(expenses.items(), key=lambda x: -x[1])):
                pct = (amt / total_exp * 100) if total_exp else 0
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.grid(row=i + 1, column=0, sticky="ew", padx=15, pady=2)
                row.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(row, text=cat, text_color=c["fg"], width=150).grid(row=0, column=0, sticky="w")
                progress = ctk.CTkProgressBar(row, width=200, progress_color=c["green"])
                progress.set(pct / 100)
                progress.grid(row=0, column=1, padx=10)
                ctk.CTkLabel(row, text=f"{amt:,.0f} {cur} ({pct:.0f}%)", text_color=c["muted"]).grid(row=0, column=2, sticky="e")
        else:
            ctk.CTkLabel(card, text="Нет данных о расходах", text_color=c["muted"]).grid(row=1, column=0, padx=15, pady=10)

        card2 = self._card(self.content)
        card2.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        card2.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card2, text="Доходы по источникам", font=ctk.CTkFont(size=13, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 10))

        if incomes:
            total_inc = sum(incomes.values())
            for i, (cat, amt) in enumerate(sorted(incomes.items(), key=lambda x: -x[1])):
                pct = (amt / total_inc * 100) if total_inc else 0
                row = ctk.CTkFrame(card2, fg_color="transparent")
                row.grid(row=i + 1, column=0, sticky="ew", padx=15, pady=2)
                row.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(row, text=cat, text_color=c["fg"], width=150).grid(row=0, column=0, sticky="w")
                progress = ctk.CTkProgressBar(row, width=200, progress_color=c["green"])
                progress.set(pct / 100)
                progress.grid(row=0, column=1, padx=10)
                ctk.CTkLabel(row, text=f"{amt:,.0f} {cur} ({pct:.0f}%)", text_color=c["muted"]).grid(row=0, column=2, sticky="e")
        else:
            ctk.CTkLabel(card2, text="Нет данных о доходах", text_color=c["muted"]).grid(row=1, column=0, padx=15, pady=10)

    # ── 4. Категории ──
    def show_categories(self):
        self._clear_content()
        self.content.grid_rowconfigure(1, weight=1)
        self._header("Категории")
        c = self.colors
        cur = self.data["settings"]["currency"]

        ctk.CTkButton(
            self.content, text="＋ Добавить категорию",
            fg_color=c["green"], text_color="#0d1a14", font=ctk.CTkFont(weight="bold"),
            command=self._add_category_dialog,
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        ctk.CTkLabel(self.content, text="Расходы", font=ctk.CTkFont(size=12, weight="bold"), text_color=c["fg"]).grid(row=2, column=0, sticky="w", padx=0, pady=(5, 5))
        exp_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        exp_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        exp_frame.grid_columnconfigure((0, 1, 2), weight=1)

        exp_cats = [cat for cat in self.data["categories"] if cat["type"] == "expense"]
        for i, cat in enumerate(exp_cats):
            card = self._card(exp_frame)
            card.grid(row=i // 3, column=i % 3, padx=(0, 10), pady=5, sticky="nsew")
            spent = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "expense" and t["category"] == cat["name"])
            ctk.CTkLabel(card, text=cat["name"], font=ctk.CTkFont(size=11, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text=f"Потрачено: {spent:,.0f} {cur}", font=ctk.CTkFont(size=9), text_color=c["muted"]).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        ctk.CTkLabel(self.content, text="Доходы", font=ctk.CTkFont(size=12, weight="bold"), text_color=c["fg"]).grid(row=4, column=0, sticky="w", padx=0, pady=(10, 5))
        inc_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        inc_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        inc_frame.grid_columnconfigure((0, 1, 2), weight=1)

        inc_cats = [cat for cat in self.data["categories"] if cat["type"] == "income"]
        for i, cat in enumerate(inc_cats):
            card = self._card(inc_frame)
            card.grid(row=0, column=i, padx=(0, 10), pady=5, sticky="nsew")
            earned = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "income" and t["category"] == cat["name"])
            ctk.CTkLabel(card, text=cat["name"], font=ctk.CTkFont(size=11, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text=f"Получено: {earned:,.0f} {cur}", font=ctk.CTkFont(size=9), text_color=c["green"]).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

    def _add_category_dialog(self):
        c = self.colors
        win = ctk.CTkToplevel(self)
        win.title("Новая категория")
        win.geometry("350x250")
        win.configure(fg_color=c["card"])
        win.resizable(False, False)

        ctk.CTkLabel(win, text="Тип:", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(20, 2))
        type_var = ctk.StringVar(value="expense")
        type_frame = ctk.CTkFrame(win, fg_color="transparent")
        type_frame.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkRadioButton(type_frame, text="Расход", variable=type_var, value="expense").pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(type_frame, text="Доход", variable=type_var, value="income").pack(side="left")

        ctk.CTkLabel(win, text="Название:", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(0, 2))
        name_entry = ctk.CTkEntry(win, fg_color=c["input_bg"], placeholder_text="")
        name_entry.pack(fill="x", padx=20, pady=(0, 15))

        def save():
            name = name_entry.get().strip()
            if not name:
                return
            self.data["categories"].append({"name": name, "type": type_var.get()})
            save_data(self.data)
            win.destroy()
            self.show_categories()

        ctk.CTkButton(win, text="💾 Сохранить", fg_color=c["green"], text_color="#0d1a14", font=ctk.CTkFont(weight="bold"), command=save).pack(pady=10)

    # ── 5. Цели ──
    def show_goals(self):
        self._clear_content()
        self.content.grid_rowconfigure(1, weight=1)
        self._header("Цели")
        c = self.colors
        cur = self.data["settings"]["currency"]

        ctk.CTkButton(
            self.content, text="＋ Создать цель",
            fg_color=c["green"], text_color="#0d1a14", font=ctk.CTkFont(weight="bold"),
            command=self._add_goal_dialog,
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        goals_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        goals_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        goals_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for i, goal in enumerate(self.data["goals"]):
            card = self._card(goals_frame)
            card.grid(row=i // 3, column=i % 3, padx=(0, 10), pady=5, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=f"{goal.get('icon', '🎯')} {goal['name']}", font=ctk.CTkFont(size=12, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 2))
            pct = min(100, (goal["current"] / goal["target"] * 100)) if goal["target"] else 0
            ctk.CTkLabel(card, text=f"{goal['current']:,.0f} / {goal['target']:,.0f} {cur}", font=ctk.CTkFont(size=11), text_color=c["fg"]).grid(row=1, column=0, sticky="w", padx=12, pady=2)
            progress = ctk.CTkProgressBar(card, progress_color=c["green"])
            progress.set(pct / 100)
            progress.grid(row=2, column=0, sticky="ew", padx=12, pady=5)
            color = c["green"] if pct >= 100 else (c["yellow"] if pct > 50 else c["red"])
            ctk.CTkLabel(card, text=f"{pct:.0f}%", font=ctk.CTkFont(size=11, weight="bold"), text_color=color).grid(row=3, column=0, sticky="e", padx=12, pady=2)

            add_frame = ctk.CTkFrame(card, fg_color="transparent")
            add_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 10))
            add_frame.grid_columnconfigure(0, weight=1)
            amt_entry = ctk.CTkEntry(add_frame, fg_color=c["input_bg"], placeholder_text="Сумма", width=100)
            amt_entry.grid(row=0, column=0, padx=(0, 5))

            def contribute(g=goal, e=amt_entry):
                try:
                    val = float(e.get())
                    if val <= 0:
                        raise ValueError
                except ValueError:
                    return
                g["current"] = g.get("current", 0) + val
                save_data(self.data)
                self.show_goals()

            ctk.CTkButton(add_frame, text="+", fg_color=c["green"], text_color="#0d1a14", width=40, command=contribute).grid(row=0, column=1)

        if not self.data["goals"]:
            ctk.CTkLabel(self.content, text="Нет целей. Создайте первую!", text_color=c["muted"], font=ctk.CTkFont(size=11)).grid(row=3, column=0, pady=30)

    def _add_goal_dialog(self):
        c = self.colors
        win = ctk.CTkToplevel(self)
        win.title("Новая цель")
        win.geometry("380x280")
        win.configure(fg_color=c["card"])
        win.resizable(False, False)

        ctk.CTkLabel(win, text="Название:", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(20, 2))
        name_entry = ctk.CTkEntry(win, fg_color=c["input_bg"])
        name_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(win, text="Целевая сумма:", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(0, 2))
        target_entry = ctk.CTkEntry(win, fg_color=c["input_bg"])
        target_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(win, text="Иконка (emoji):", text_color=c["fg"]).pack(anchor="w", padx=20, pady=(0, 2))
        icon_entry = ctk.CTkEntry(win, fg_color=c["input_bg"])
        icon_entry.insert(0, "🎯")
        icon_entry.pack(fill="x", padx=20, pady=(0, 15))

        def save():
            name = name_entry.get().strip()
            try:
                target = float(target_entry.get())
                if target <= 0:
                    raise ValueError
            except ValueError:
                return
            if not name:
                return
            self.data["goals"].append({
                "name": name,
                "target": target,
                "current": 0,
                "icon": icon_entry.get() or "🎯",
            })
            save_data(self.data)
            win.destroy()
            self.show_goals()

        ctk.CTkButton(win, text="💾 Создать", fg_color=c["green"], text_color="#0d1a14", font=ctk.CTkFont(weight="bold"), command=save).pack(pady=5)

    # ── 6. Настройки ──
    def show_settings(self):
        self._clear_content()
        self.content.grid_rowconfigure(1, weight=1)
        self._header("Настройки")
        c = self.colors

        card = self._card(self.content)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="Валюта", font=ctk.CTkFont(size=11, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 5))
        cur_var = ctk.StringVar(value=self.data["settings"]["currency"])
        cur_menu = ctk.CTkOptionMenu(card, variable=cur_var, values=["KGS", "RUB", "USD", "EUR"])
        cur_menu.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        card2 = self._card(self.content)
        card2.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        card2.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card2, text="Тема", font=ctk.CTkFont(size=11, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 5))
        theme_var = ctk.StringVar(value=self.data["settings"]["theme"])
        theme_frame = ctk.CTkFrame(card2, fg_color="transparent")
        theme_frame.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))
        ctk.CTkRadioButton(theme_frame, text="🌙 Тёмная", variable=theme_var, value="dark").pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(theme_frame, text="☀️ Светлая", variable=theme_var, value="light").pack(side="left")

        card3 = self._card(self.content)
        card3.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        notif_var = ctk.BooleanVar(value=self.data["settings"]["notifications"])
        ctk.CTkCheckBox(card3, text="Включить уведомления", variable=notif_var).grid(row=0, column=0, sticky="w", padx=15, pady=12)

        def save_settings():
            self.data["settings"]["currency"] = cur_var.get()
            self.data["settings"]["theme"] = theme_var.get()
            self.data["settings"]["notifications"] = notif_var.get()
            save_data(self.data)
            self.colors = DARK if theme_var.get() == "dark" else LIGHT
            ctk.set_appearance_mode("dark" if theme_var.get() == "dark" else "light")
            self.configure(fg_color=self.colors["bg"])
            self.sidebar.configure(fg_color=self.colors["sidebar"])
            for w in self.sidebar.winfo_children():
                w.destroy()
            self._build_sidebar()
            self.show_settings()

        ctk.CTkButton(self.content, text="💾 Сохранить изменения", fg_color=c["green"], text_color="#0d1a14", font=ctk.CTkFont(weight="bold"), command=save_settings).grid(row=4, column=0, sticky="w", pady=10)

    # ── 7. Справка ──
    def show_help(self):
        self._clear_content()
        self.content.grid_rowconfigure(1, weight=1)
        self._header("Справка / Помощь")
        c = self.colors
        sections = [
            ("❓ Как добавлять транзакции",
             "Перейдите в раздел «Транзакции» и нажмите «Добавить доход» или «Добавить расход». Заполните категорию, сумму и дату, затем нажмите «Сохранить»."),
            ("🏷️ Как создавать категории",
             "В разделе «Категории» нажмите «Добавить категорию». Укажите название и тип (доход/расход)."),
            ("🎯 Как ставить цели",
             "В разделе «Цели» нажмите «Создать цель». Укажите название и целевую сумму. Пополняйте цель, вводя сумму и нажимая «+»."),
            ("📈 Как смотреть аналитику",
             "Раздел «Аналитика» показывает распределение расходов и доходов по категориям с процентами."),
        ]
        for i, (title, text) in enumerate(sections):
            card = self._card(self.content)
            card.grid(row=i + 1, column=0, sticky="ew", pady=(0, 10))
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=c["fg"]).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))
            ctk.CTkLabel(card, text=text, font=ctk.CTkFont(size=10), text_color=c["muted"], justify="left").grid(row=1, column=0, sticky="w", padx=15, pady=(0, 12))


# ─── Запуск ──────────────────────────────────────────────
if __name__ == "__main__":
    theme = load_data().get("settings", {}).get("theme", "dark")
    ctk.set_appearance_mode("dark" if theme == "dark" else "light")
    app = FinanceApp()
    app.mainloop()

