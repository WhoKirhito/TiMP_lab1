import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import time
from typing import List, Optional
import webbrowser
import tempfile


class MenuItem:
    
    
    def __init__(self, name: str, price: float, prep_time: time):
        self.name = name
        self.price = price
        self.prep_time = prep_time
    
    def to_tuple(self):
        return (self.name, f"{self.price:.2f}", self.prep_time.strftime('%H:%M'))


class MenuApp:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Управление меню")
        self.root.geometry("600x500")
        
        self.items: List[MenuItem] = []
        self.current_file: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть", command=self.load_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Таблица
        columns = ("Название", "Цена", "Время")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки (3 кнопки)
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="HTML страница", command=self.open_html).pack(side=tk.LEFT, padx=5)
        
        
        self.status = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN)
        self.status.pack(fill=tk.X, padx=10, pady=5)
    
    def refresh_table(self):
        """Обновление таблицы."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for menu_item in self.items:
            self.tree.insert("", tk.END, values=menu_item.to_tuple())
        
        self.status.config(text=f"Всего: {len(self.items)} пунктов")
    
    def load_file(self):
        """Загрузка из файла."""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filename:
            return
        
        try:
            self.items.clear()
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Парсинг: Меню "Название" 350.50 12:30
                        match = re.match(r'Меню\s+"([^"]+)"\s+([\d.]+)\s+(\d+:\d+)', line)
                        if match:
                            name, price, time_str = match.groups()
                            h, m = map(int, time_str.split(':'))
                            self.items.append(MenuItem(name, float(price), time(h, m)))
            
            self.current_file = filename
            self.refresh_table()
            self.status.config(text=f"Загружен: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def save_file(self):
        """Сохранение в файл."""
        if not self.current_file:
            filename = filedialog.asksaveasfilename(defaultextension=".txt")
            if not filename:
                return
            self.current_file = filename
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                for item in self.items:
                    f.write(f'Меню "{item.name}" {item.price:.2f} {item.prep_time.strftime("%H:%M")}\n')
            self.status.config(text=f"Сохранен: {self.current_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def add_item(self):
      
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Цена:").grid(row=1, column=0, padx=5, pady=5)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Время (ЧЧ:ММ):").grid(row=2, column=0, padx=5, pady=5)
        time_entry = ttk.Entry(dialog)
        time_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save():
            try:
                name = name_entry.get().strip()
                price = float(price_entry.get())
                h, m = map(int, time_entry.get().split(':'))
                self.items.append(MenuItem(name, price, time(h, m)))
                self.refresh_table()
                dialog.destroy()
                self.status.config(text=f"Добавлен: {name}")
            except:
                messagebox.showerror("Ошибка", "Неверный формат")
        
        ttk.Button(dialog, text="OK", command=save).grid(row=3, column=0, columnspan=2, pady=10)
    
    def delete_item(self):
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пункт")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить?"):
            index = self.tree.index(selection[0])
            deleted = self.items.pop(index)
            self.refresh_table()
            self.status.config(text=f"Удален: {deleted.name}")
    
    def open_html(self):
        if not self.items:
            messagebox.showinfo("Информация", "Нет данных")
            return
        
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Меню</title>
</head>
<body>
    <h1>Меню ресторана</h1>
    
    <table border="1" cellpadding="5" cellspacing="0">
        <thead>
            <tr>
                <th>Название</th>
                <th>Цена</th>
                <th>Время приготовления</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for item in self.items:
            html_content += f"""
            <tr>
                <td>{item.name}</td>
                <td>{item.price:.2f} ₽</td>
                <td>{item.prep_time.strftime('%H:%M')}</td>
            </tr>
"""
        
        html_content += f"""
        </tbody>
    </table>
    
    <br>
    <p>Всего блюд: {len(self.items)}</p>
    <br>
    
    <button onclick="window.close()">Назад</button>
    
    <script>

    </script>
</body>
</html>
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                        encoding='utf-8', delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        webbrowser.open(f'file://{temp_file}')
        self.status.config(text="HTML страница открыта")
    
    def run(self):
        """Запуск приложения."""
        self.root.mainloop()


def main():
    """Главная функция."""
    app = MenuApp()
    app.run()


if __name__ == "__main__":
    main()
