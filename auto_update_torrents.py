#!/usr/bin/env python3

"""
Скрипт для автоматической проверки новых серий на AniLiberty
и обновления торрентов в qBittorrent Web API
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update_torrents.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """Конфигурация приложения"""

    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Загрузка конфигурации из файла"""
        if not os.path.exists(self.config_path):
            default_config = {
                "aniliberty": {
                    "api_url": "https://aniliberty.top/api/v1",
                    "check_interval": 300
                },
                "qbittorrent": {
                    "url": "http://localhost:8080",
                    "username": "admin",
                    "password": "adminadmin",
                    "download_path": ""
                },
                "tracked_releases": {}
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            logger.info(f"Создан файл конфигурации: {self.config_path}")
            return default_config

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_config(self):
        """Сохранение конфигурации в файл"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)


class AniLibertyAPI:
    """Клиент для работы с AniLiberty API"""

    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()

    def get_release_torrents(self, release_id: int) -> List[Dict]:
        """Получить список торрентов для релиза"""
        try:
            url = f"{self.api_url}/anime/torrents/release/{release_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении торрентов для релиза {release_id}: {e}")
            return []

    def get_torrent_file(self, hash_or_id: str, save_path: str) -> bool:
        """Скачать торрент-файл"""
        try:
            url = f"{self.api_url}/anime/torrents/{hash_or_id}/file"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Торрент-файл сохранен: {save_path}")
            return True
        except requests.RequestException as e:
            logger.error(f"Ошибка при скачивании торрент-файла {hash_or_id}: {e}")
            return False

    def get_release_info(self, release_id: int) -> Optional[Dict]:
        """Получить информацию о релизе"""
        try:
            url = f"{self.api_url}/anime/releases/{release_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении информации о релизе {release_id}: {e}")
            return None

    def search_releases(self, query: str, limit: int = 10) -> List[Dict]:
        """Поиск релизов по названию"""
        try:
            # ИСПРАВЛЕНИЕ: используем правильный endpoint /app/search/releases с параметром query
            url = f"{self.api_url}/app/search/releases"
            params = {'query': query}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Ответ — массив релизов напрямую, обрезаем до limit
            if isinstance(data, list):
                return data[:limit]
            return data.get('data', [])[:limit]
        except requests.RequestException as e:
            logger.error(f"Ошибка при поиске релизов: {e}")
            return []


class QBittorrentAPI:
    """Клиент для работы с qBittorrent Web API"""

    def __init__(self, url: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.logged_in = False

    def login(self) -> bool:
        """Авторизация в qBittorrent"""
        try:
            response = self.session.post(
                f"{self.url}/api/v2/auth/login",
                data={'username': self.username, 'password': self.password},
                timeout=10
            )
            if response.status_code == 200 and response.text == 'Ok.':
                self.logged_in = True
                logger.info("Успешная авторизация в qBittorrent")
                return True
            elif response.status_code == 204:
                self.logged_in = True
                logger.info("Успешная авторизация в qBittorrent")
                return True
            else:
                logger.error(f"Ошибка авторизации в qBittorrent: {response.status_code} {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"Ошибка при подключении к qBittorrent: {e}")
            return False

    def get_torrents(self) -> List[Dict]:
        """Получить список всех торрентов"""
        if not self.logged_in and not self.login():
            return []
        try:
            response = self.session.get(f"{self.url}/api/v2/torrents/info", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении списка торрентов: {e}")
            return []

    def add_torrent(self, torrent_path: str, category: str = None, save_path: str = None) -> bool:
        """Добавить торрент"""
        if not self.logged_in and not self.login():
            return False
        try:
            with open(torrent_path, 'rb') as f:
                files = {'torrents': f}
                data = {}
                if category:
                    data['category'] = category
                if save_path:
                    data['savepath'] = save_path

                response = self.session.post(
                    f"{self.url}/api/v2/torrents/add",
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.text == 'Ok.':
                logger.info(f"Торрент успешно добавлен: {torrent_path}")
                return True

            if response.text == 'Conflict':
                logger.info(f"Торрент уже существует в qBittorrent: {torrent_path}")
                return True

            try:
                result = response.json()
                if result.get('success_count', 0) > 0:
                    logger.info(f"Торрент успешно добавлен: {torrent_path}")
                    return True
                elif result.get('failure_count', 0) > 0:
                    logger.error(f"Ошибка при добавлении торрента: {response.text}")
                    return False
            except Exception:
                pass

            logger.error(f"Неожиданный ответ при добавлении торрента: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении торрента: {e}")
            return False

    def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> bool:
        """Удалить торрент"""
        if not self.logged_in and not self.login():
            return False
        try:
            # ИСПРАВЛЕНИЕ: приводим хэш к нижнему регистру — qBittorrent хранит хэши в нижнем регистре
            torrent_hash = torrent_hash.lower()
            response = self.session.post(
                f"{self.url}/api/v2/torrents/delete",
                data={
                    'hashes': torrent_hash,
                    'deleteFiles': 'true' if delete_files else 'false'
                },
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Торрент удален: {torrent_hash}")
                return True
            else:
                logger.error(f"Ошибка при удалении торрента: {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"Ошибка при удалении торрента: {e}")
            return False

    def find_torrent_by_name(self, name: str) -> Optional[Dict]:
        """Найти торрент по имени"""
        torrents = self.get_torrents()
        for torrent in torrents:
            if name.lower() in torrent['name'].lower():
                return torrent
        return None


class TorrentUpdater:
    """Основной класс для обновления торрентов"""

    def __init__(self, config: Config):
        self.config = config
        self.aniliberty = AniLibertyAPI(config.config['aniliberty']['api_url'])
        qb_config = config.config['qbittorrent']
        self.qbittorrent = QBittorrentAPI(
            qb_config['url'],
            qb_config['username'],
            qb_config['password']
        )
        self.temp_dir = Path('temp_torrents')
        self.temp_dir.mkdir(exist_ok=True)
        self.state_file = 'state.json'
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Загрузить состояние из файла"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_state(self):
        """Сохранить состояние в файл"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def check_release_updates(self, release_id: int) -> Optional[Dict]:
        """Проверить обновления для релиза"""
        logger.info(f"Проверка обновлений для релиза {release_id}")

        torrents = self.aniliberty.get_release_torrents(release_id)
        if not torrents:
            logger.warning(f"Не найдено торрентов для релиза {release_id}")
            return None

        # Сортируем по дате обновления, берем самые свежие
        torrents.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

        # Среди торрентов с самой свежей датой выбираем самый легкий
        latest_date = torrents[0].get('updated_at', '')
        latest_torrents = [t for t in torrents if t.get('updated_at', '') == latest_date]
        latest_torrent = min(latest_torrents, key=lambda x: x.get('size', float('inf')))

        size_mb = latest_torrent.get('size', 0) / (1024 * 1024)
        logger.info(f"  Выбран торрент: {latest_torrent.get('label', 'N/A')}")
        logger.info(f"  Размер: {size_mb:.2f} MB")

        # ИСПРАВЛЕНИЕ: нормализуем хэш к нижнему регистру для сравнения
        new_hash = latest_torrent['hash'].lower()

        release_key = str(release_id)
        if release_key in self.state:
            last_hash = self.state[release_key].get('hash', '').lower()
            if last_hash == new_hash:
                logger.info(f"Релиз {release_id} не обновлялся")
                return None

            logger.info(f"Найдено обновление для релиза {release_id}")
            logger.info(f"  Старый hash: {last_hash}")
            logger.info(f"  Новый hash: {new_hash}")
            logger.info(f"  Описание: {latest_torrent.get('description', 'N/A')}")
        else:
            logger.info(f"Релиз {release_id} добавлен в отслеживание")

        return latest_torrent

    def update_torrent(self, release_id: int, new_torrent: Dict, save_path: str = None) -> bool:
        """Обновить торрент в qBittorrent"""
        release_key = str(release_id)

        # ИСПРАВЛЕНИЕ: нормализуем хэш к нижнему регистру
        new_hash = new_torrent['hash'].lower()

        # Скачиваем новый торрент-файл
        torrent_filename = f"release_{release_id}_{new_hash}.torrent"
        torrent_path = self.temp_dir / torrent_filename

        if not self.aniliberty.get_torrent_file(new_hash, str(torrent_path)):
            return False

        # Если есть старый торрент, удаляем его
        if release_key in self.state:
            old_hash = self.state[release_key].get('qb_hash')
            if old_hash:
                logger.info(f"Удаление старого торрента: {old_hash}")
                # delete_torrent уже нормализует хэш внутри себя
                self.qbittorrent.delete_torrent(old_hash, delete_files=False)

        # Добавляем новый торрент
        category = f"AniLiberty_{release_id}"
        if self.qbittorrent.add_torrent(str(torrent_path), category, save_path):
            # Обновляем состояние — всегда сохраняем хэш в нижнем регистре
            self.state[release_key] = {
                'hash': new_hash,
                'updated_at': new_torrent.get('updated_at'),
                'description': new_torrent.get('description'),
                'qb_hash': new_hash,
                'last_check': datetime.now().isoformat(),
                'save_path': save_path or ''
            }
            self._save_state()

            try:
                os.remove(torrent_path)
            except Exception:
                pass

            return True

        return False

    def run_check(self):
        """Выполнить проверку всех отслеживаемых релизов"""
        tracked_releases = self.config.config.get('tracked_releases', {})

        if not tracked_releases:
            logger.warning("Нет отслеживаемых релизов в конфигурации")
            return

        logger.info(f"Начало проверки {len(tracked_releases)} релизов")

        for release_id, release_config in tracked_releases.items():
            try:
                release_id = int(release_id)
                save_path = release_config.get('save_path') if isinstance(release_config, dict) else None

                if not save_path:
                    save_path = self.config.config['qbittorrent'].get('download_path', '')

                new_torrent = self.check_release_updates(release_id)
                if new_torrent:
                    logger.info(f"Обновление торрента для релиза {release_id}")
                    if self.update_torrent(release_id, new_torrent, save_path):
                        logger.info(f"✓ Релиз {release_id} успешно обновлен")
                    else:
                        logger.error(f"✗ Ошибка при обновлении релиза {release_id}")

                time.sleep(2)

            except Exception as e:
                logger.error(f"Ошибка при обработке релиза {release_id}: {e}")

        logger.info("Проверка завершена")

    def run_loop(self):
        """Запустить бесконечный цикл проверки"""
        check_interval = self.config.config['aniliberty'].get('check_interval', 300)
        logger.info(f"Запуск мониторинга с интервалом {check_interval} секунд")

        while True:
            try:
                self.run_check()
            except Exception as e:
                logger.error(f"Критическая ошибка в цикле проверки: {e}")

            logger.info(f"Следующая проверка через {check_interval} секунд")
            time.sleep(check_interval)


def main():
    """Главная функция"""
    import argparse

    parser = argparse.ArgumentParser(description='Автоматическое обновление торрентов с AniLiberty')
    parser.add_argument('--config', default='config.json', help='Путь к файлу конфигурации')
    parser.add_argument('--once', action='store_true', help='Выполнить одну проверку и выйти')
    parser.add_argument('--add-release', type=int, help='Добавить релиз в отслеживание по ID')
    parser.add_argument('--search', type=str, help='Найти релиз по названию')
    parser.add_argument('--add-by-name', type=str, help='Добавить релиз по названию (интерактивный выбор)')
    parser.add_argument('--save-path', type=str, help='Путь сохранения для добавляемого релиза')

    args = parser.parse_args()

    config = Config(args.config)
    aniliberty = AniLibertyAPI(config.config['aniliberty']['api_url'])

    # Поиск релизов по названию
    if args.search:
        results = aniliberty.search_releases(args.search)
        if not results:
            print("Релизы не найдены")
            return

        print(f"\nНайдено релизов: {len(results)}\n")
        for i, release in enumerate(results, 1):
            name = release['name']['main']
            english = release['name'].get('english', '')
            year = release.get('year', 'N/A')
            release_type = release['type']['description']
            episodes = release.get('episodes_total', '?')

            print(f"{i}. ID: {release['id']}")
            print(f"   Название: {name}")
            if english:
                print(f"   English: {english}")
            print(f"   Год: {year} | Тип: {release_type} | Эпизодов: {episodes}")
            print()
        return

    # Добавление релиза по названию с интерактивным выбором
    if args.add_by_name:
        results = aniliberty.search_releases(args.add_by_name)
        if not results:
            print("Релизы не найдены")
            return

        print(f"\nНайдено релизов: {len(results)}\n")
        for i, release in enumerate(results, 1):
            name = release['name']['main']
            english = release['name'].get('english', '')
            year = release.get('year', 'N/A')

            print(f"{i}. {name}")
            if english:
                print(f"   ({english})")
            print(f"   ID: {release['id']} | Год: {year}")
            print()

        try:
            choice = int(input("Выберите номер релиза (0 для отмены): "))
            if choice == 0:
                print("Отменено")
                return

            if 1 <= choice <= len(results):
                selected = results[choice - 1]
                release_id = selected['id']
                release_name = selected['name']['main']

                save_path = args.save_path
                if not save_path:
                    save_path = input(f"Путь сохранения для '{release_name}' (Enter для пути по умолчанию): ").strip()

                release_key = str(release_id)
                if release_key not in config.config['tracked_releases']:
                    config.config['tracked_releases'][release_key] = {
                        'name': release_name,
                        'save_path': save_path
                    }
                    config.save_config()
                    print(f"\n✓ Релиз '{release_name}' (ID: {release_id}) добавлен в отслеживание")
                    if save_path:
                        print(f"  Путь сохранения: {save_path}")
                else:
                    print(f"\n✗ Релиз '{release_name}' уже отслеживается")
            else:
                print("Неверный номер")
        except (ValueError, KeyboardInterrupt):
            print("\nОтменено")
        return

    # Добавление релиза по ID
    if args.add_release:
        release_key = str(args.add_release)
        release_info = aniliberty.get_release_info(args.add_release)
        release_name = release_info['name']['main'] if release_info else f"Release {args.add_release}"

        if release_key not in config.config['tracked_releases']:
            save_path = args.save_path or ''
            config.config['tracked_releases'][release_key] = {
                'name': release_name,
                'save_path': save_path
            }
            config.save_config()
            print(f"✓ Релиз '{release_name}' (ID: {args.add_release}) добавлен в отслеживание")
            if save_path:
                print(f"  Путь сохранения: {save_path}")
        else:
            print(f"✗ Релиз '{release_name}' уже отслеживается")
        return

    updater = TorrentUpdater(config)

    if args.once:
        updater.run_check()
    else:
        updater.run_loop()


if __name__ == '__main__':
    main()