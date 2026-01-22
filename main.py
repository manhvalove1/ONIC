import tkinter as tk

app = tk.Tk()
app.title("Наше приложение")
app.geometry("400x300")

label = tk.Label(app, text="Привет! Это desktop-приложение 😎")
label.pack(pady=20)

app.mainloop()
