import tkinter as tk
from tkinter import messagebox

class SettingsDialog:
    def __init__(self, settings):
        self.settings = settings
        self.result = False
        
        self.dialog = tk.Tk()
        self.dialog.title("Настройки")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        y = 20
        
        tk.Label(self.dialog, text="Ширина окна:").place(x=20, y=y)
        self.txt_width = tk.Entry(self.dialog, width=20)
        self.txt_width.place(x=180, y=y)
        self.txt_width.insert(0, str(self.settings.window_width))
        
        y += 35
        tk.Label(self.dialog, text="Высота окна:").place(x=20, y=y)
        self.txt_height = tk.Entry(self.dialog, width=20)
        self.txt_height.place(x=180, y=y)
        self.txt_height.insert(0, str(self.settings.window_height))
        
        y += 35
        tk.Label(self.dialog, text="Название игры:").place(x=20, y=y)
        self.txt_title = tk.Entry(self.dialog, width=20)
        self.txt_title.place(x=180, y=y)
        self.txt_title.insert(0, self.settings.game_title)
        
        y += 35
        tk.Label(self.dialog, text="Скорость танка:").place(x=20, y=y)
        self.txt_tank_speed = tk.Entry(self.dialog, width=20)
        self.txt_tank_speed.place(x=180, y=y)
        self.txt_tank_speed.insert(0, str(self.settings.tank_speed))
        
        y += 35
        tk.Label(self.dialog, text="Скорость пуль:").place(x=20, y=y)
        self.txt_bullet_speed = tk.Entry(self.dialog, width=20)
        self.txt_bullet_speed.place(x=180, y=y)
        self.txt_bullet_speed.insert(0, str(self.settings.bullet_speed))
        
        y += 35
        tk.Label(self.dialog, text="Урон пуль:").place(x=20, y=y)
        self.txt_bullet_damage = tk.Entry(self.dialog, width=20)
        self.txt_bullet_damage.place(x=180, y=y)
        self.txt_bullet_damage.insert(0, str(self.settings.bullet_damage))
        
        y += 35
        tk.Label(self.dialog, text="Файл уровня:").place(x=20, y=y)
        self.txt_level = tk.Entry(self.dialog, width=20)
        self.txt_level.place(x=180, y=y)
        self.txt_level.insert(0, self.settings.default_level)
        
        y += 45
        btn_ok = tk.Button(self.dialog, text="OK", width=10, command=self.on_ok)
        btn_ok.place(x=150, y=y)
        
        btn_cancel = tk.Button(self.dialog, text="Отмена", width=10, command=self.on_cancel)
        btn_cancel.place(x=250, y=y)
    
    def on_ok(self):
        try:
            self.settings.window_width = int(self.txt_width.get())
            self.settings.window_height = int(self.txt_height.get())
            self.settings.game_title = self.txt_title.get()
            self.settings.tank_speed = float(self.txt_tank_speed.get())
            self.settings.bullet_speed = float(self.txt_bullet_speed.get())
            self.settings.bullet_damage = int(self.txt_bullet_damage.get())
            self.settings.default_level = self.txt_level.get()
            
            self.result = True
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка ввода: {e}")
    
    def on_cancel(self):
        self.result = False
        self.dialog.destroy()
    
    def show(self):
        self.dialog.mainloop()
        return self.result