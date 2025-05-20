import libtorrent as lt
import time
import datetime

class BitTorrentClient:
    def __init__(self):
        """
        Инициализация BitTorrent-клиента.
        Создаем сессию и устанавливаем настройки.
        """
        # Настройки сессии
        self.settings = {
            'listen_interfaces': '0.0.0.0:6881',  # Интерфейс и порт для входящих соединений
            'download_rate_limit': 0,             # Лимит загрузки (0 - без лимита)
            'upload_rate_limit': 0,              # Лимит отдачи (0 - без лимита)
            'alert_mask': lt.alert.category_t.all_categories,  # Получать все уведомления
        }
        
        # Создаем сессию с настройками
        self.session = lt.session()
        self.session.apply_settings(self.settings)
        
        # Словарь для хранения активных загрузок
        self.torrents = {}
    
    def add_torrent(self, torrent_file_path, save_path='/home/andrew/Desktop/Visual-Studio-CODE/Course-work/course-alpha/download'):
        """
        Добавляет торрент для загрузки.
        
        :param torrent_file_path: Путь к .torrent файлу
        :param save_path: Директория для сохранения загруженных файлов
        :return: Идентификатор торрента (info_hash)
        """
        # Параметры загрузки
        params = {
            'ti': lt.torrent_info(torrent_file_path),
            'save_path': save_path,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        }
        
        # Добавляем торрент в сессию
        handle = self.session.add_torrent(params)
        info_hash = str(handle.info_hash())
        
        # Сохраняем информацию о торренте
        self.torrents[info_hash] = {
            'handle': handle,
            'status': None,
            'added_time': datetime.datetime.now(),
            'save_path': save_path
        }
        
        print(f"Торрент добавлен. Info hash: {info_hash}")
        return info_hash
    
    def add_magnet_link(self, magnet_link, save_path='./downloads'):
        """
        Добавляет торрент по magnet-ссылке.
        
        :param magnet_link: Magnet-ссылка
        :param save_path: Директория для сохранения загруженных файлов
        :return: Идентификатор торрента (info_hash)
        """
        # Парсим magnet-ссылку
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = save_path
        params.storage_mode = lt.storage_mode_t.storage_mode_sparse
        
        # Добавляем торрент в сессию
        handle = self.session.add_torrent(params)
        info_hash = str(handle.info_hash())
        
        # Сохраняем информацию о торренте
        self.torrents[info_hash] = {
            'handle': handle,
            'status': None,
            'added_time': datetime.datetime.now(),
            'save_path': save_path
        }
        
        print(f"Magnet-ссылка добавлена. Info hash: {info_hash}")
        return info_hash
    
    def update_torrent_status(self, info_hash):
        """
        Обновляет статус торрента.
        
        :param info_hash: Идентификатор торрента
        :return: Актуальный статус или None если торрент не найден
        """
        if info_hash not in self.torrents:
            return None
        
        handle = self.torrents[info_hash]['handle']
        status = handle.status()
        
        # Сохраняем обновленный статус
        self.torrents[info_hash]['status'] = status
        return status
    
    def get_torrent_progress(self, info_hash):
        """
        Возвращает прогресс загрузки торрента в процентах.
        
        :param info_hash: Идентификатор торрента
        :return: Прогресс от 0 до 100 или None если торрент не найден
        """
        if info_hash not in self.torrents:
            return None
        
        status = self.update_torrent_status(info_hash)
        if status:
            return status.progress * 100
        return 0
    
    def get_torrent_info(self, info_hash):
        """
        Возвращает информацию о торренте.
        
        :param info_hash: Идентификатор торрента
        :return: Словарь с информацией или None если торрент не найден
        """
        if info_hash not in self.torrents:
            return None
        
        status = self.update_torrent_status(info_hash)
        if not status:
            return None
        
        handle = self.torrents[info_hash]['handle']
        torrent_info = handle.get_torrent_info()
        
        return {
            'name': torrent_info.name(),
            'info_hash': info_hash,
            'progress': status.progress * 100,
            'download_rate': status.download_rate / 1000,  # KB/s
            'upload_rate': status.upload_rate / 1000,      # KB/s
            'total_download': status.total_download / 1000000,  # MB
            'total_upload': status.total_upload / 1000000,       # MB
            'num_peers': status.num_peers,
            'state': str(status.state),
            'save_path': self.torrents[info_hash]['save_path'],
            'added_time': self.torrents[info_hash]['added_time'],
        }
    
    def remove_torrent(self, info_hash, remove_files=False):
        """
        Удаляет торрент из сессии.
        
        :param info_hash: Идентификатор торрента
        :param remove_files: Удалять ли загруженные файлы
        """
        if info_hash in self.torrents:
            self.session.remove_torrent(self.torrents[info_hash]['handle'], remove_files)
            del self.torrents[info_hash]
            print(f"Торрент {info_hash} удален")
    
    def main_loop(self):
        """
        Основной цикл клиента для обработки событий и обновления статусов.
        """
        print("BitTorrent клиент запущен. Ожидание событий...")
        
        try:
            while True:
                # Обрабатываем уведомления
                alerts = self.session.pop_alerts()
                for alert in alerts:
                    print(f"[Alert] {alert.message()}")
                
                # Обновляем статусы всех торрентов
                for info_hash in list(self.torrents.keys()):
                    info = self.get_torrent_info(info_hash)
                    if info:
                        print(f"\nТоррент: {info['name']}")
                        print(f"Прогресс: {info['progress']:.2f}%")
                        print(f"Скачивание: {info['download_rate']:.1f} KB/s")
                        print(f"Отдача: {info['upload_rate']:.1f} KB/s")
                        print(f"Пиры: {info['num_peers']}")
                
                time.sleep(5)  # Пауза между обновлениями
                
        except KeyboardInterrupt:
            print("\nОстановка клиента...")
            self.session.pause()
            for info_hash in list(self.torrents.keys()):
                self.remove_torrent(info_hash)


if __name__ == "__main__":
    # Пример использования клиента
    
    client = BitTorrentClient()
    
    # Загрузка по .torrent файлу
    torrent_id = client.add_torrent("/home/andrew/Desktop/Visual-Studio-CODE/Course-work/course-alpha/Signalis.torrent")
    
    # Запускаем основной цикл
    client.main_loop()