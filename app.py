import time
import requests
from datetime import datetime
import yadisk
import json


class VKAPIClient:  # Создаю класс, который может взаимодействовать с данными пользователя из ВК
    '''Класс, являющийся клиентом к API VK '''

    API_BASE_URL = 'https://api.vk.com/method'  # Базовый URL

    def __init__(self, token, user_id) -> None:  # Инициализация классас 2-я параметрами
        self.token = token
        self.user_id = user_id
        self.params = {
            'access_token': self.token,  # Token
            'v': '5.131'  # Версия VK
        }

    def _build_url(self, api_metod):  # Метод с 1 параметром, возвращающий базовый URL + параметр
        return f'{self.API_BASE_URL}/{api_metod}'

    def get_profile_photo(self):  # Метод получает информацию о фото профиля пользователя
        self.params.update(
            {'owner_id': self.user_id,  # Дополняю словарь с общ. парам. ID пользователя и ID альбома с фото
             'album_id': 'profile',
             'photo_sizes': 1,
             'extended': 1
             })
        response = requests.get(self._build_url('photos.get'),
                                params=self.params).json()  # отправляю GET-запрос и присваиваю его в формате JSON к переменной

        return response  # Возвращаю данные из запроса


class Yandex:
    count = 0  # счетик для остановки копирования фото

    def __init__(self, token):
        self.token = token
        self.y = yadisk.YaDisk(token=token)
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def create_folder(self):
        '''Создание папки'''

        try:  # Если папки нет, то создает 'VK_photos_backup'
            self.folder_name = 'VK_profile_photo'
            self.y.mkdir(self.folder_name)
        except:  # Иначе создает с другим именем

            self.folder_name = 'VK_profile_photo(1)'
            self.y.mkdir(self.folder_name)

    def create_json(self):
        self.json_data = []
        with open('info.json', 'w') as file:
            file.write(json.dumps(self.json_data))

    def upload_to_disk(self, count_photo=5):
        '''Загрузка на диск'''
        self.count_photo = count_photo

        j = vk.get_profile_photo()  # Получение данных о фото в json-формате
        path_photo = j['response']['items']  # Переходит к нужному месту в json

        print('Progress:')

        for i in path_photo:  # Вывод нужного URL и даты-времени в string
            dt = datetime.fromtimestamp(i['date'])  # Перевод метки времени в читабельный формат даты_времени
            str_date_time = dt.strftime("%d_%m_%Y_%H_%M_%S")  # Форматирование времени-даты для имени фото

            for s in i['sizes']:  # Проход циклом по спискам в ['sizes']
                if self.count != self.count_photo:  # Если счетчик не равен счетчику по умолчанию/введенному пользователем
                    if s['type'] == 'x':
                        self.y.upload_url(s['url'],
                                          f'/{self.folder_name}/{str_date_time}')  # Загружает фото на диск и именует "дата_время"
                        self.count += 1  # Добавляет к счетчику +1
                        file_info = {'file_name': str_date_time, 'size': s['type']}  # Словарь с данными о фото
                        with open('info.json', 'r') as f:  # Открывает файл json для чтения

                            json_file = json.load(f)  # Присваивает переменной объект из json
                            json_file.append(file_info)  # обавляет в список словарь с данными о фото
                            with open('info.json', 'w', encoding='utf-8') as f:  # Открытие на запись
                                json.dump(json_file, f)  # Добавление данных в json file

                            print(f'Photo "{str_date_time}" was uploaded in "{self.folder_name}"', end='\n')

        print('Success!')


if __name__ == '__main__':  # Создаю конструктор для выполнения кода только в нем

    print('Hello! Your backup APP is ready')
    time.sleep(1)

    vk_token = input('Enter VK token:\n')
    yandex_token = input('Enter Yandex token:\n')
    vk_id = int(input('Enter VK ID:\n'))
    photo_count = input('How many photos do you want to copy(default - 5)?\nPress "Enter" to skip:\n')

    vk = VKAPIClient(vk_token, vk_id)  # Экземпляр  VKAPIClient с параметрами TOKEN и ID пользователя
    yandex = Yandex(yandex_token)  # Экземпляр Yandex с параметром токена

    yandex.create_json()
    yandex.create_folder()

    if photo_count:
        yandex.upload_to_disk(int(photo_count))
    else:
        yandex.upload_to_disk()
