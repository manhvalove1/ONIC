
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime, timedelta
import json
import os
import platform
import sys
from pathlib import Path
import csv
import webbrowser

class UniversalFinanceTracker:
    def __init__(self, root):
        self.root = root
        
        # Определяем операционную систему
        self.os_name = platform.system()
        self.is_windows = (self.os_name == 'Windows')
        self.is_mac = (self.os_name == 'Darwin')
        self.is_linux = (self.os_name == 'Linux')
        
        print(f"Запуск на {self.os_name}")
        
        # Настройка для разных ОС
        self.setup_os_specific()
        
        # Настройка окна
        self.setup_window()
        
        # Инициализация
        self.init_variables()
        self.setup_paths()
        self.init_db()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        self.load_data()
        
        # Центрирование окна
        self.center_window()
    
    def setup_os_specific(self):
        """Настройки для конкретных ОС"""
        # Шрифты
        if self.is_windows:
            self.font_family = 'Segoe UI'
            self.title_size = 22
            self.normal_size = 10
            self.large_size = 24
            
            # Стиль кнопок для Windows
            ttk.Style().theme_use('vista')
            
        elif self.is_mac:
            self.font_family = 'Helvetica'
            self.title_size = 24
            self.normal_size = 12
            self.large_size = 26
            
            # Увеличиваем отступы для macOS
            self.pad_x = 15
            self.pad_y = 10
            
        else:  # Linux
            self.font_family = 'Ubuntu'
            self.title_size = 22
            self.normal_size = 10
            self.large_size = 24
            
            # Попробуем использовать Ubuntu стиль
            try:
                ttk.Style().theme_use('clam')
            except:
                pass
        
        # Размеры окна
        if self.is_windows:
            self.window_size = "1100x700"
        elif self.is_mac:
            self.window_size = "1200x750"
        else:
            self.window_size = "1100x700"
    
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("💰 Personal Finance Tracker - Windows/Linux/macOS")
        self.root.geometry(self.window_size)
        
        # Иконка (если есть)
        self.set_window_icon()
        
        # Цвет фона
        bg_color = '#f0f0f0' if self.is_windows else '#f6f6f6'
        self.root.configure(bg=bg_color)
        
        # Запрет изменения размеров
        self.root.resizable(True, True)
    
    def set_window_icon(self):
        """Установка иконки окна"""
        try:
            if self.is_windows:
                self.root.iconbitmap(default='icon.ico')
            else:
                # Для Linux/macOS можно использовать PNG
                icon_path = self.get_resource_path('icon.png')
                if os.path.exists(icon_path):
                    img = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, img)
        except:
            pass  # Если нет иконки - не страшно
    
    def get_resource_path(self, filename):
        """Получение пути к ресурсам (для pyinstaller)"""
        if hasattr(sys, '_MEIPASS'):
            # Мы в собранном exe
            return os.path.join(sys._MEIPASS, filename)
        else:
            # Мы в исходном коде
            return filename
    
    def setup_paths(self):
        """Настройка путей к данным"""
        if self.is_windows:
            base_dir = Path(os.environ.get('APPDATA', Path.home()))
            self.app_dir = base_dir / 'PersonalFinanceTracker'
            
        elif self.is_mac:
            base_dir = Path.home() / 'Library' / 'Application Support'

self.app_dir = base_dir / 'com.yourcompany.financetracker'
            
        else:  # Linux
            base_dir = Path.home() / '.local' / 'share'
            self.app_dir = base_dir / 'finance-tracker'
        
        # Создаем папки
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        # Пути к файлам
        self.db_file = self.app_dir / 'transactions.db'
        self.settings_file = self.app_dir / 'settings.json'
        self.export_dir = self.app_dir / 'exports'
        self.export_dir.mkdir(exist_ok=True)
    
    def init_variables(self):
        """Инициализация переменных"""
        # Язык и валюта
        self.language = "ru"
        self.currency = "RUB"
        
        # Словари
        self.currency_symbols = {
            "RUB": "₽", "USD": "$", "EUR": "€", 
            "GBP": "£", "CNY": "¥", "JPY": "¥"
        }
        
        # Цвета (адаптивные)
        self.colors = {
            'primary': '#E95420' if self.is_linux else '#0078D7',
            'secondary': '#77216F' if self.is_linux else '#4CAF50',
            'income': '#2ECC71',
            'expense': '#E74C3C',
            'bg_light': '#f6f6f6',
            'bg_dark': '#2d2d2d',
            'text_light': '#ffffff',
            'text_dark': '#333333'
        }
        
        # Переводы (упрощенные)
        self.translations = {
            "ru": {
                "app_title": "💰 Трекер финансов",
                "add": "Добавить",
                "delete": "Удалить",
                "income": "Доход",
                "expense": "Расход",
                "balance": "Баланс",
                "settings": "Настройки"
            },
            "en": {
                "app_title": "💰 Finance Tracker",
                "add": "Add",
                "delete": "Delete",
                "income": "Income",
                "expense": "Expense",
                "balance": "Balance",
                "settings": "Settings"
            }
        }
    
    def init_db(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect(str(self.db_file))
        self.cursor = self.conn.cursor()
        
        # Таблица транзакций
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Индексы для быстрого поиска
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON transactions(date)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON transactions(type)')
        
        self.conn.commit()
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Верхняя панель
        self.create_top_bar()
        
        # Основная область
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая колонка - форма и быстрые действия
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Правая колонка - история и статистика
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Форма добавления
        self.create_add_form(left_frame)
        
        # Быстрые действия
        self.create_quick_actions(left_frame)
        
        # Статистика
        self.create_statistics(right_frame)
        
        # История
        self.create_history(right_frame)
        
        # Статус бар
        self.create_status_bar()
    
    def create_top_bar(self):
        """Создание верхней панели"""
        top_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        top_frame.pack(fill=tk.

X, padx=5, pady=5)
        
        # Заголовок
        title_label = tk.Label(top_frame,
                              text=self.t("app_title"),
                              font=(self.font_family, self.title_size, 'bold'),
                              fg=self.colors['primary'])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT, padx=20)
        
        # Кнопка настроек
        settings_btn = ttk.Button(button_frame,
                                 text=self.t("settings"),
                                 command=self.open_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка помощи
        help_btn = ttk.Button(button_frame,
                             text="?",
                             width=3,
                             command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=5)
    
    def create_add_form(self, parent):
        """Создание формы добавления транзакции"""
        form_frame = ttk.LabelFrame(parent, text="➕ Новая транзакция", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Сетка формы
        row = 0
        
        # Тип
        ttk.Label(form_frame, text="Тип:").grid(row=row, column=0, sticky='w', pady=5)
        self.type_var = tk.StringVar(value='expense')
        
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=row, column=1, columnspan=2, sticky='w', pady=5)
        
        ttk.Radiobutton(type_frame, text="Расход", variable=self.type_var,
                       value='expense').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Доход", variable=self.type_var,
                       value='income').pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Категория
        ttk.Label(form_frame, text="Категория:").grid(row=row, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame,
                                         textvariable=self.category_var,
                                         width=20,
                                         state='readonly')
        self.category_combo.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        row += 1
        
        # Сумма и валюта
        ttk.Label(form_frame, text="Сумма:").grid(row=row, column=0, sticky='w', pady=5)
        
        amount_frame = ttk.Frame(form_frame)
        amount_frame.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        self.amount_var = tk.StringVar()
        ttk.Entry(amount_frame,
                 textvariable=self.amount_var,
                 width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        self.currency_var = tk.StringVar(value=self.currency)
        currency_combo = ttk.Combobox(amount_frame,
                                     textvariable=self.currency_var,
                                     values=list(self.currency_symbols.keys()),
                                     width=8,
                                     state='readonly')
        currency_combo.pack(side=tk.LEFT)
        
        row += 1
        
        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=row, column=0, sticky='w', pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(form_frame,
                 textvariable=self.desc_var,
                 width=30).grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        
        row += 1
        
        # Кнопка добавления
        add_btn = ttk.Button(form_frame,
                           text="Добавить",
                           command=self.add_transaction,
                           style='Accent.TButton')
        add_btn.grid(row=row, column=0, columnspan=3, pady=15, sticky='ew')
        
        # Стиль для акцентной кнопки
        style = ttk.Style()
        style.configure('Accent.TButton',
                       background=self.colors['primary'],

foreground='white',
                       font=(self.font_family, self.normal_size, 'bold'))
    
    def create_quick_actions(self, parent):
        """Создание панели быстрых действий"""
        actions_frame = ttk.LabelFrame(parent, text="⚡ Быстрые действия", padding=15)
        actions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Кнопки быстрых доходов
        ttk.Label(actions_frame, text="Быстрые доходы:").pack(anchor='w', pady=(0, 5))
        
        income_frame = ttk.Frame(actions_frame)
        income_frame.pack(fill=tk.X, pady=(0, 15))
        
        income_amounts = [100, 500, 1000, 5000]
        for amount in income_amounts:
            btn = ttk.Button(income_frame,
                           text=f"💰 +{amount}",
                           command=lambda a=amount: self.quick_add('income', a))
            btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Кнопки быстрых расходов
        ttk.Label(actions_frame, text="Быстрые расходы:").pack(anchor='w', pady=(0, 5))
        
        expense_frame = ttk.Frame(actions_frame)
        expense_frame.pack(fill=tk.X)
        
        expense_amounts = [100, 200, 500, 1000]
        for amount in expense_amounts:
            btn = ttk.Button(expense_frame,
                           text=f"🛒 -{amount}",
                           command=lambda a=amount: self.quick_add('expense', a))
            btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
    
    def create_statistics(self, parent):
        """Создание панели статистики"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Статистика", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Сетка статистики
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Доходы
        income_card = ttk.Frame(stats_grid, relief=tk.RAISED, borderwidth=1)
        income_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        ttk.Label(income_card, text="Доходы:", font=(self.font_family, 9)).pack(pady=(10, 0))
        self.income_label = ttk.Label(income_card,
                                     text="0.00 ₽",
                                     font=(self.font_family, self.large_size, 'bold'),
                                     foreground=self.colors['income'])
        self.income_label.pack(pady=(5, 10))
        
        # Расходы
        expense_card = ttk.Frame(stats_grid, relief=tk.RAISED, borderwidth=1)
        expense_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        ttk.Label(expense_card, text="Расходы:", font=(self.font_family, 9)).pack(pady=(10, 0))
        self.expense_label = ttk.Label(expense_card,
                                      text="0.00 ₽",
                                      font=(self.font_family, self.large_size, 'bold'),
                                      foreground=self.colors['expense'])
        self.expense_label.pack(pady=(5, 10))
        
        # Баланс
        balance_card = ttk.Frame(stats_grid, relief=tk.RAISED, borderwidth=1)
        balance_card.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
        
        ttk.Label(balance_card, text="Баланс:", font=(self.font_family, 9)).pack(pady=(10, 0))
        self.balance_label = ttk.Label(balance_card,
                                      text="0.00 ₽",
                                      font=(self.font_family, self.large_size, 'bold'),
                                      foreground=self.colors['primary'])
        self.balance_label.pack(pady=(5, 10))
        
        # Выравнивание
        for i in range(3):
            stats_grid.columnconfigure(i, weight=1)
    
    def create_history(self, parent):
        """Создание панели истории транзакций"""
        history_frame = ttk.LabelFrame(parent, text="📝 История", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель управления
        controls_frame = ttk.Frame(history_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

# Кнопки
        ttk.Button(controls_frame,
                  text="🗑️ Удалить",
                  command=self.delete_transaction).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame,
                  text="📤 Экспорт",
                  command=self.export_data).pack(side=tk.LEFT)
        
        # Treeview с историей
        columns = ('date', 'type', 'category', 'amount', 'desc')
        self.tree = ttk.Treeview(history_frame,
                                columns=columns,
                                show='headings',
                                height=15,
                                selectmode='browse')
        
        # Заголовки
        self.tree.heading('date', text='Дата')
        self.tree.heading('type', text='Тип')
        self.tree.heading('category', text='Категория')
        self.tree.heading('amount', text='Сумма')
        self.tree.heading('desc', text='Описание')
        
        # Ширина колонок
        self.tree.column('date', width=100)
        self.tree.column('type', width=80)
        self.tree.column('category', width=120)
        self.tree.column('amount', width=100)
        self.tree.column('desc', width=200)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame,
                                 orient=tk.VERTICAL,
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка событий
        self.tree.bind('<Double-1>', self.on_item_double_click)
    
    def create_status_bar(self):
        """Создание статус-бара"""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar,
                                     text="Готово | Записей: 0",
                                     relief=tk.SUNKEN,
                                     anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def t(self, key):
        """Функция перевода"""
        return self.translations.get(self.language, {}).get(key, key)
    
    def load_data(self):
        """Загрузка данных"""
        self.update_categories()
        self.update_statistics()
        self.update_history()
        self.update_status()
    
    def update_categories(self):
        """Обновление списка категорий"""
        categories = ['Еда', 'Транспорт', 'Жилье', 'Развлечения', 
                     'Здоровье', 'Одежда', 'Зарплата', 'Фриланс']
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.current(0)
    
    def update_statistics(self):
        """Обновление статистики"""
        # Заглушка - в реальном приложении здесь запрос к БД
        self.income_label.config(text="10,000.00 ₽")
        self.expense_label.config(text="7,500.00 ₽")
        self.balance_label.config(text="2,500.00 ₽")
    
    def update_history(self):
        """Обновление истории"""
        # Очистка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление тестовых данных
        test_data = [
            ('2024-01-15', 'income', 'Зарплата', '+50,000.00 ₽', 'Январь'),
            ('2024-01-16', 'expense', 'Еда', '-2,500.00 ₽', 'Продукты'),
            ('2024-01-17', 'expense', 'Транспорт', '-1,200.00 ₽', 'Такси'),
            ('2024-01-18', 'income', 'Фриланс', '+15,000.

00 ₽', 'Заказ')
        ]
        
        for data in test_data:
            self.tree.insert('', 'end', values=data)
    
    def update_status(self):
        """Обновление статус-бара"""
        count = len(self.tree.get_children())
        self.status_label.config(text=f"Готово | Записей: {count}")
    
    def add_transaction(self):
        """Добавление транзакции"""
        try:
            amount = float(self.amount_var.get())
            category = self.category_var.get()
            trans_type = self.type_var.get()
            currency = self.currency_var.get()
            description = self.desc_var.get()
            date = datetime.now().strftime('%Y-%m-%d')
            
            # Сохранение в БД
            self.cursor.execute('''
                INSERT INTO transactions (date, type, category, amount, currency, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, trans_type, category, amount, currency, description))
            
            self.conn.commit()
            
            # Очистка полей
            self.amount_var.set('')
            self.desc_var.set('')
            
            # Обновление
            self.load_data()
            
            messagebox.showinfo("Успех", "Транзакция добавлена!")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
    
    def quick_add(self, trans_type, amount):
        """Быстрое добавление"""
        self.type_var.set(trans_type)
        self.amount_var.set(str(amount))
        self.category_var.set('Быстрая запись' if trans_type == 'income' else 'Еда')
        self.desc_var.set('Быстрое добавление')
        self.add_transaction()
    
    def delete_transaction(self):
        """Удаление транзакции"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите транзакцию для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную транзакцию?"):
            # Здесь будет удаление из БД
            self.tree.delete(selection[0])
            self.update_status()
            messagebox.showinfo("Успех", "Транзакция удалена")
    
    def on_item_double_click(self, event):
        """Двойной клик по записи"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            messagebox.showinfo("Детали", f"Вы выбрали:\n{values}")
    
    def export_data(self):
        """Экспорт данных"""
        filename = self.export_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Дата', 'Тип', 'Категория', 'Сумма', 'Валюта', 'Описание'])
            
            # Здесь нужно получить данные из БД
            # writer.writerow([...])
        
        messagebox.showinfo("Экспорт", f"Данные экспортированы в:\n{filename}")
    
    def open_settings(self):
        """Открытие настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Центрирование
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="Настройки",
                 font=(self.font_family, 16, 'bold')).pack(pady=20)
        
        # Язык
        ttk.Label(settings_window, text="Язык:").pack(anchor='w', padx=40, pady=5)
        lang_var = tk.StringVar(value=self.language)
        
        lang_frame = ttk.Frame(settings_window)
        lang_frame.pack(padx=40, fill=tk.X)
        
        ttk.Radiobutton(lang_frame, text="Русский",
                       variable=lang_var, value='ru').pack(side=tk.LEFT, padx=10)
        ttk.


Radiobutton(lang_frame, text="English",
                       variable=lang_var, value='en').pack(side=tk.LEFT, padx=10)
        
        # Валюта
        ttk.Label(settings_window, text="Валюта:").pack(anchor='w', padx=40, pady=15)
        currency_var = tk.StringVar(value=self.currency)
        
        currency_combo = ttk.Combobox(settings_window,
                                     textvariable=currency_var,
                                     values=list(self.currency_symbols.keys()),
                                     state='readonly',
                                     width=10)
        currency_combo.pack(anchor='w', padx=40)
        
        # Кнопки
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=30)
        
        def save_settings():
            self.language = lang_var.get()
            self.currency = currency_var.get()
            self.load_data()
            settings_window.destroy()
            messagebox.showinfo("Сохранено", "Настройки сохранены")
        
        ttk.Button(button_frame, text="Сохранить",
                  command=save_settings).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Отмена",
                  command=settings_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def show_help(self):
        """Показать справку"""
        help_text = f"""
        Финансовый трекер v1.0
        --------------------
        Платформа: {self.os_name}
        Python: {sys.version}
        
        Использование:
        1. Выберите тип (доход/расход)
        2. Выберите категорию
        3. Введите сумму и валюту
        4. Добавьте описание (необязательно)
        5. Нажмите "Добавить"
        
        Быстрые действия:
        - Двойной клик: просмотр деталей
        - Выделить + Удалить: удаление
        - Экспорт: сохранение в CSV
        
        Автор: Ваше имя
        Лицензия: MIT
        """
        
        messagebox.showinfo("Справка", help_text)

def main():
    """Главная функция"""
    try:
        root = tk.Tk()
        app = UniversalFinanceTracker(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение:\n{str(e)}")

if name == "__main__":
    main()
