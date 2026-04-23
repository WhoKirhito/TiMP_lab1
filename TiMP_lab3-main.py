import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import time, datetime
import webbrowser
import tempfile
import os


# ==================== ЛОГГЕР ====================
class Logger:
    def __init__(self):
        if not os.path.exists("logs"):
            os.makedirs("logs")
    
    def log_error(self, msg):
        with open("logs/errors.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - ERROR - {msg}\n")


# ==================== МОДЕЛЬ ====================
class MenuItem:
    def __init__(self, name, price, prep_time):
        if not name or not name.strip():
            raise ValueError("Название не может быть пустым")
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
        self.name = name.strip()
        self.price = price
        self.prep_time = prep_time
    
    def __str__(self):
        return f'Меню "{self.name}" {self.price:.2f} {self.prep_time.strftime("%H:%M")}'


class MenuModel:
    def __init__(self):
        self.items = []
        self.current_file = None
        self.logger = Logger()
    
    def add(self, name, price, prep_time):
        self.items.append(MenuItem(name, price, prep_time))
    
    def delete(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        raise IndexError("Неверный индекс")
    
    def parse_line(self, line):
        line = line.strip()
        if not line:
            return None
        try:
            match = re.match(r'Меню\s+"([^"]+)"\s+([\d.]+)\s+(\d+:\d+)', line)
            if not match:
                raise ValueError("Неверный формат")
            name = match.group(1)
            price = float(match.group(2))
            h, m = map(int, match.group(3).split(':'))
            return MenuItem(name, price, time(h, m))
        except Exception as e:
            self.logger.log_error(f"Ошибка парсинга '{line}': {e}")
            return None
    
    def load(self, filename):
        self.items.clear()
        success = 0
        errors = 0
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                item = self.parse_line(line)
                if item:
                    self.items.append(item)
                    success += 1
                else:
                    errors += 1
        self.current_file = filename
        return success, errors
    
    def save(self, filename=None):
        target = filename or self.current_file
        if not target:
            raise ValueError("Нет файла для сохранения")
        with open(target, 'w', encoding='utf-8') as f:
            for item in self.items:
                f.write(str(item) + '\n')
        self.current_file = target
        return target
    
    def to_html(self):
        if not self.items:
            return "<p>Нет данных</p>"
        rows = ""
        for item in self.items:
            rows += f"""
                <tr>
                    <td>{item.name}</td>
                    <td>{item.price:.2f} ₽</td>
                    <td>{item.prep_time.strftime('%H:%M')}</td>
                </tr>
            """
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Меню</title>
<style>table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #ddd;padding:8px}} th{{background:#f2f2f2}}</style>
</head><body><h1>Меню</h1>
<table><thead><tr><th>Название</th><th>Цена</th><th>Время</th></tr></thead><tbody>{rows}</tbody></table>
<p><strong>Всего: {len(self.items)}</strong></p><button onclick="window.close()">Закрыть</button>
</body></html>"""


# ==================== ДИАЛОГ ДОБАВЛЕНИЯ ====================
class AddDialog:
    def __init__(self, parent):
        self.result = None
        self.dlg = tk.Toplevel(parent)
        self.dlg.title("Добавить")
        self.dlg.geometry("300x180")
        self.dlg.transient(parent)
        self.dlg.grab_set()
        
        tk.Label(self.dlg, text="Название:").place(x=15, y=15)
        self.entry_name = ttk.Entry(self.dlg, width=25)
        self.entry_name.place(x=100, y=15)
        
        tk.Label(self.dlg, text="Цена:").place(x=15, y=50)
        self.entry_price = ttk.Entry(self.dlg, width=25)
        self.entry_price.place(x=100, y=50)
        
        tk.Label(self.dlg, text="Время (ЧЧ:ММ):").place(x=15, y=85)
        self.entry_time = ttk.Entry(self.dlg, width=25)
        self.entry_time.place(x=115, y=85)
        
        ttk.Button(self.dlg, text="OK", command=self.ok).place(x=80, y=130)
        ttk.Button(self.dlg, text="Отмена", command=self.cancel).place(x=170, y=130)
        
        self.entry_name.focus()
    
    def ok(self):
        try:
            name = self.entry_name.get().strip()
            if not name:
                raise ValueError("Введите название")
            price = float(self.entry_price.get())
            if price <= 0:
                raise ValueError("Цена > 0")
            parts = self.entry_time.get().split(':')
            if len(parts) != 2:
                raise ValueError("Формат ЧЧ:ММ")
            self.result = (name, price, time(int(parts[0]), int(parts[1])))
            self.dlg.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def cancel(self):
        self.dlg.destroy()


# ==================== ГЛАВНОЕ ОКНО ====================
class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Меню — TiMP Lab3")
        self.root.geometry("600x500")
        
        self.model = MenuModel()
        
        # Меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть", command=self.load)
        file_menu.add_command(label="Сохранить", command=self.save)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Таблица
        self.tree = ttk.Treeview(self.root, columns=("Название", "Цена", "Время"), show="headings")
        for col in ("Название", "Цена", "Время"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Добавить", command=self.add).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="HTML", command=self.html).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN)
        self.status.pack(fill=tk.X, padx=10, pady=5)
        
        self.refresh()
    
    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.model.items:
            self.tree.insert("", tk.END, values=(item.name, f"{item.price:.2f}", item.prep_time.strftime("%H:%M")))
        self.status.config(text=f"Всего: {len(self.model.items)}")
    
    def load(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if not f:
            return
        try:
            ok, err = self.model.load(f)
            self.refresh()
            self.status.config(text=f"Загружено: {ok}, ошибок: {err}")
            if err:
                self.status.config(text=f"Ошибок: {err} (см. logs/errors.log)", foreground="red")
            else:
                self.status.config(foreground="black")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def save(self):
        try:
            if not self.model.current_file:
                f = filedialog.asksaveasfilename(defaultextension=".txt")
                if not f:
                    return
                self.model.save(f)
            else:
                self.model.save()
            self.status.config(text=f"Сохранено: {self.model.current_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def add(self):
        dlg = AddDialog(self.root)
        self.root.wait_window(dlg.dlg)
        if dlg.result:
            name, price, t = dlg.result
            try:
                self.model.add(name, price, t)
                self.refresh()
                self.status.config(text=f"Добавлен: {name}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
    
    def delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Выберите пункт")
            return
        if messagebox.askyesno("Подтверждение", "Удалить?"):
            idx = self.tree.index(sel[0])
            deleted = self.model.delete(idx)
            self.refresh()
            self.status.config(text=f"Удалён: {deleted.name}")
    
    def html(self):
        if not self.model.items:
            messagebox.showinfo("Инфо", "Нет данных")
            return
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as f:
            f.write(self.model.to_html())
            webbrowser.open(f'file://{f.name}')
        self.status.config(text="HTML открыт")
    
    def run(self):
        self.root.mainloop()


# ==================== ТОЧКА ВХОДА ====================
if __name__ == "__main__":
    app = MainApp()
    app.run()
