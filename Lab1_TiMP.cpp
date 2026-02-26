from datetime import time
import re

class MenuItem:
    """Класс для представления пункта меню"""
    def __init__(self, name, price, prep_time):
        self.name = name
        self.price = price
        self.prep_time = prep_time
    
    def __str__(self):
        return f"Пункт меню: {self.name}, Цена: {self.price:.2f}, " \
               f"Время приготовления: {self.prep_time.strftime('%H:%M')}"


def parse_object(obj_string):
    """
    Парсит строку с описанием объекта и создает объект MenuItem.
    """
    # Разделяем строку на части, сохраняя строки в кавычках
    pattern = r'"([^"]*)"|(\S+)'
    parts = []
    
    for match in re.finditer(pattern, obj_string):
        parts.append(match.group(1) or match.group(2))
    
    # Используем match для проверки структуры
    match parts:
        case []:
            raise ValueError("Пустая строка")
        
        case [obj_type, name, price_str, time_str]:
            if obj_type not in ["Меню", "Menu"]:
                raise ValueError(f"Ожидается 'Меню' или 'Menu', получено '{obj_type}'")
            
            if not name:
                raise ValueError("Название не может быть пустым")
            
            try:
                price = float(price_str)
                h, m = map(int, time_str.split(':'))
                prep_time = time(h, m)
            except:
                raise ValueError("Некорректный формат цены или времени")
            
            return MenuItem(name, price, prep_time)
        
        case _:
            raise ValueError(f"Должно быть 3 свойства, получено {len(parts)-1}")


def main():
    """Основная функция программы"""
    print("Вариант: Меню (название, цена, время приготовления)")
    print('Формат: Меню "Название" Цена ЧЧ:ММ')
    print('Пример: Меню "Борщ" 350.50 12:30')
    print('Для выхода введите пустую строку')
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nВведите строку: ").strip()
            
            if not user_input:
                print("Программа завершена.")
                break
            
            obj = parse_object(user_input)
            print(f" Создан объект: {obj}")
            
        except (EOFError, KeyboardInterrupt):
            print("\nПрограмма завершена.")
            break
        except Exception as e:
            print(f" Ошибка: {e}")


if __name__ == "__main__":
    main()