import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from coursecore import BitTorrentClient
import time
import threading

class BitTorrentClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BitTorrent Client")
        self.root.geometry("900x600")
        
        # Инициализация клиента
        self.client = BitTorrentClient()
        
        # Запуск основного цикла в отдельном потоке
        self.running = True
        self.client_thread = threading.Thread(target=self.run_client_loop, daemon=True)
        self.client_thread.start()
        
        # Создание элементов интерфейса
        self.create_widgets()
        
        # Привязка события закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Секция добавления торрента
        add_frame = ttk.LabelFrame(main_frame, text="Добавить торрент", padding="10")
        add_frame.pack(fill=tk.X, pady=5)
        
        # Кнопка добавления торрент-файла
        ttk.Button(add_frame, text="Добавить файл торрента", command=self.add_torrent_file).pack(side=tk.LEFT, padx=5)
        
        # Поле ввода и кнопка для magnet-ссылки
        magnet_frame = ttk.Frame(add_frame)
        magnet_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.magnet_entry = ttk.Entry(magnet_frame)
        self.magnet_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(magnet_frame, text="Добавить Magnet-ссылку", command=self.add_magnet_link).pack(side=tk.LEFT)
        
        # Список активных торрентов
        list_frame = ttk.LabelFrame(main_frame, text="Активные торренты", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Таблица для отображения торрентов
        columns = ("name", "progress", "download", "upload", "peers", "state", "hash")
        self.torrent_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        
        # Настройка колонок
        self.torrent_tree.heading("name", text="Имя")
        self.torrent_tree.heading("progress", text="Прогресс")
        self.torrent_tree.heading("download", text="Скачивание (KB/s)")
        self.torrent_tree.heading("upload", text="Отдача (KB/s)")
        self.torrent_tree.heading("peers", text="Пиры")
        self.torrent_tree.heading("state", text="Состояние")
        self.torrent_tree.heading("hash", text="Хэш")
        
        self.torrent_tree.column("name", width=200, anchor=tk.W)
        self.torrent_tree.column("progress", width=80, anchor=tk.CENTER)
        self.torrent_tree.column("download", width=80, anchor=tk.CENTER)
        self.torrent_tree.column("upload", width=80, anchor=tk.CENTER)
        self.torrent_tree.column("peers", width=60, anchor=tk.CENTER)
        self.torrent_tree.column("state", width=100, anchor=tk.CENTER)
        self.torrent_tree.column("hash", width=150, anchor=tk.W)
        
        self.torrent_tree.pack(fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.torrent_tree.yview)
        self.torrent_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель управления и деталей
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Кнопка просмотра деталей
        ttk.Button(control_frame, text="Показать детали", command=self.show_details).pack(side=tk.LEFT, padx=5)
        
        # Кнопка удаления торрента
        ttk.Button(control_frame, text="Удалить торрент", command=self.remove_torrent).pack(side=tk.LEFT, padx=5)
        
        # Кнопка удаления торрента с файлами
        ttk.Button(
            control_frame, 
            text="Удалить торрент + файлы", 
            command=lambda: self.remove_torrent(remove_files=True)
        ).pack(side=tk.LEFT, padx=5)
        
        # Строка состояния
        self.status_var = tk.StringVar()
        self.status_var.set("Готов")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, pady=5)
    
    def add_torrent_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл торрента",
            filetypes=[("Torrent files", "*.torrent"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                info_hash = self.client.add_torrent(file_path)
                self.status_var.set(f"Добавлен торрент: {info_hash}")
                self.update_torrent_list()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить торрент: {str(e)}")
    
    def add_magnet_link(self):
        magnet_link = self.magnet_entry.get().strip()
        if not magnet_link:
            messagebox.showwarning("Предупреждение", "Введите magnet-ссылку")
            return
        
        try:
            info_hash = self.client.add_magnet_link(magnet_link)
            self.status_var.set(f"Добавлена magnet-ссылка: {info_hash}")
            self.magnet_entry.delete(0, tk.END)
            self.update_torrent_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить magnet-ссылку: {str(e)}")
    
    def update_torrent_list(self):
        # Очистка текущего списка
        for item in self.torrent_tree.get_children():
            self.torrent_tree.delete(item)
        
        # Добавление торрентов в список
        for info_hash in self.client.torrents:
            info = self.client.get_torrent_info(info_hash)
            if info:
                self.torrent_tree.insert("", tk.END, values=(
                    info['name'],
                    f"{info['progress']:.1f}%",
                    f"{info['download_rate']:.1f}",
                    f"{info['upload_rate']:.1f}",
                    info['num_peers'],
                    info['state'],
                    info_hash
                ))
    
    def get_selected_torrent(self):
        selection = self.torrent_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите торрент")
            return None
        
        item = self.torrent_tree.item(selection[0])
        return item['values'][-1]  # Хэш находится в последней колонке
    
    def show_details(self):
        info_hash = self.get_selected_torrent()
        if not info_hash:
            return
        
        info = self.client.get_torrent_info(info_hash)
        if not info:
            messagebox.showerror("Ошибка", "Не удалось получить информацию о торренте")
            return
        
        details = (
            f"Имя: {info['name']}\n"
            f"Хэш: {info['info_hash']}\n"
            f"Прогресс: {info['progress']:.2f}%\n"
            f"Скорость загрузки: {info['download_rate']:.1f} KB/s\n"
            f"Скорость отдачи: {info['upload_rate']:.1f} KB/s\n"
            f"Всего скачано: {info['total_download']:.2f} MB\n"
            f"Всего отдано: {info['total_upload']:.2f} MB\n"
            f"Пиров: {info['num_peers']}\n"
            f"Состояние: {info['state']}\n"
            f"Путь сохранения: {info['save_path']}\n"
            f"Время добавления: {info['added_time']}"
        )
        
        messagebox.showinfo("Детали торрента", details)
    
    def remove_torrent(self, remove_files=False):
        info_hash = self.get_selected_torrent()
        if not info_hash:
            return
        
        try:
            self.client.remove_torrent(info_hash, remove_files)
            self.update_torrent_list()
            self.status_var.set(f"Удален торрент: {info_hash}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить торрент: {str(e)}")
    
    def run_client_loop(self):
        while self.running:
            try:
                # Периодическое обновление списка торрентов
                self.root.after(0, self.update_torrent_list)
                time.sleep(2)
            except:
                break
    
    def on_close(self):
        self.running = False
        if self.client_thread.is_alive():
            self.client_thread.join(timeout=1)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BitTorrentClientGUI(root)
    root.mainloop()