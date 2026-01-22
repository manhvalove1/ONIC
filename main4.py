import tkinter as tk
from tkinter import messagebox
import sqlite3

# ------------------ База данных ------------------
conn = sqlite3.connect("finance_users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()
conn.close()

current_user = ""  # глобальная переменная для текущего пользователя
frame_main = None  # глобальный фрейм для основного контента

# ------------------ Функции регистрации и входа ------------------
def register():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    if username == "" or password == "":
        messagebox.showerror("Ошибка", "Введите логин и пароль")
        return
    conn = sqlite3.connect("finance_users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Успех", "Пользователь зарегистрирован!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Такой логин уже существует")
    conn.close()

def login():
    global current_user
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    if username == "" or password == "":
        messagebox.showerror("Ошибка", "Введите логин и пароль")
        return
    conn = sqlite3.connect("finance_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        current_user = username
        messagebox.showinfo("Успех", f"Добро пожаловать, {username}!")
        root.destroy()
        open_main_app()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

# ------------------ Главное приложение ------------------
def open_main_app():
    global frame_main, current_user
    main = tk.Tk()
    main.title(f"Личный Финансовый Трекер - {current_user}")
    main.geometry("900x600")
    main.configure(bg="#1e1e1e")

    # ------------------ Боковая панель ------------------
    frame_sidebar = tk.Frame(main, bg="#2e2e2e", width=200)
    frame_sidebar.pack(side="left", fill="y")

    frame_main = tk.Frame(main, bg="#1e1e1e")
    frame_main.pack(side="left", fill="both", expand=True)

    buttons = {}

    screens = ["Мои финансы", "Аналитика", "Доходы", "Расходы", "Категории", "Цели", "Настройки", "Справка"]

    def select_screen(screen_name):
        for btn in buttons:
            buttons[btn].configure(bg="#2e2e2e")
        buttons[screen_name].configure(bg="#00FF00")
        for widget in frame_main.winfo_children():
            widget.destroy()
        if screen_name == "Настройки":
            show_settings()
        else:
            tk.Label(frame_main, text=f"Экран: {screen_name}", fg="#FFFFFF", bg="#1e1e1e", font=("Arial", 20)).pack(pady=50)

    for screen in screens:
        btn = tk.Button(frame_sidebar, text=screen, fg="#FFFFFF", bg="#2e2e2e",
                        font=("Arial", 12), relief="flat",
                        command=lambda s=screen: select_screen(s))
        btn.pack(fill="x", pady=5, padx=10)
        buttons[screen] = btn

    # ------------------ Настройки аккаунта ------------------
    def show_settings():
        global current_user, frame_main
        for widget in frame_main.winfo_children():
            widget.destroy()

        tk.Label(frame_main, text="Настройки", fg="#00FF00", bg="#1e1e1e", font=("Arial", 18)).pack(pady=20)

        # ------------------ Кнопка "Об аккаунте" ------------------
        def show_account_fields():
            # предотвращаем дублирование полей
            if hasattr(frame_main, "account_fields_shown") and frame_main.account_fields_shown:
                return
            frame_main.account_fields_shown = True
tk.Label(frame_main, text="Новый логин:", fg="#FFFFFF", bg="#1e1e1e").pack(pady=5)
            entry_new_username = tk.Entry(frame_main)
            entry_new_username.pack(pady=5)

            tk.Label(frame_main, text="Новый пароль:", fg="#FFFFFF", bg="#1e1e1e").pack(pady=5)
            entry_new_password = tk.Entry(frame_main, show="*")
            entry_new_password.pack(pady=5)

            def save_changes():
                global current_user
                new_username = entry_new_username.get().strip()
                new_password = entry_new_password.get().strip()
                if new_username == "" or new_password == "":
                    messagebox.showerror("Ошибка", "Введите новые данные")
                    return
                try:
                    conn = sqlite3.connect("finance_users.db")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET username=?, password=? WHERE username=?",
                                   (new_username, new_password, current_user))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Успех", "Данные изменены")
                    current_user = new_username
                    main.title(f"Личный Финансовый Трекер - {current_user}")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Ошибка", "Такой логин уже существует")

            tk.Button(frame_main, text="Сохранить изменения", bg="#00FF00", fg="#1e1e1e", command=save_changes).pack(pady=10)

        btn_account = tk.Button(frame_main, text="Об аккаунте", bg="#5555FF", fg="#FFFFFF", command=show_account_fields)
        btn_account.pack(pady=10)

        # ------------------ Удаление аккаунта ------------------
        def delete_account():
            global current_user
            confirm = messagebox.askyesno("Удалить аккаунт", f"Вы уверены, что хотите удалить аккаунт {current_user}?")
            if confirm:
                conn = sqlite3.connect("finance_users.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username=?", (current_user,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Удалено", "Аккаунт удалён")
                main.destroy()

        tk.Button(frame_main, text="Удалить аккаунт", bg="#FF5555", fg="#1e1e1e", command=delete_account).pack(pady=5)

    main.mainloop()

# ------------------ Окно входа / регистрации ------------------
root = tk.Tk()
root.title("Вход / Регистрация")
root.geometry("400x250")
root.configure(bg="#1e1e1e")

tk.Label(root, text="Логин:", fg="#FFFFFF", bg="#1e1e1e").pack(pady=(20,5))
entry_username = tk.Entry(root)
entry_username.pack(pady=5)

tk.Label(root, text="Пароль:", fg="#FFFFFF", bg="#1e1e1e").pack(pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

btn_login = tk.Button(root, text="Войти", bg="#00FF00", fg="#1e1e1e", command=login)
btn_login.pack(pady=(15,5))

btn_register = tk.Button(root, text="Зарегистрироваться", bg="#FFAA00", fg="#1e1e1e", command=register)
btn_register.pack(pady=5)

root.mainloop()