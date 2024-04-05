import requests
import datetime
import yadisk
import json
import logging
from settings import VK_TOKEN, VK_ID, YANDEX_TOKEN
from requests.exceptions import ConnectionError
import os.path

logging.basicConfig(level=logging.INFO, filename='py_log.log', filemode='a')


class Main:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, vk_token, vk_id, yandex_token):
        self.photo_count = 0  # счетчик для остановки копирования фото
        self.vk_token = vk_token
        self.vk_id = vk_id
        self.yandex_token = yandex_token
        self.y = yadisk.YaDisk(token=yandex_token)

        self.vk_params = {
            'access_token': self.vk_token,
            'v': '5.131'}

        self.yandex_params = {
            'Authorization': f'OAuth {self.yandex_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'}

        self.json_data = {}
        self.folder_name = ''
        self.file_name = ''
        self.json_file = ''

        # Конструктор URL

    # Конструктор URL
    def _build_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'

    # Проверка доступа к данным пользователя
    def user_get(self):
        return requests.get(self._build_url('users.get'),
                            params=self.vk_params).json()

    # Проверка токена ВК
    def check_vk_token(self):
        response = requests.get(f'https://api.vk.com/method/users.get',
                                params=self.vk_params).json()
        try:
            str(response['response'][0]['id']) == self.vk_id
            return True
        except:
            logging.error(f'{datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")} Wrong vk token')
            return False

    # Проверка токена Яндекс
    def check_yandex_token(self):
        self.y = yadisk.YaDisk(token=self.yandex_token)
        if self.y.check_token():
            return True
        else:
            logging.error(f'{datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")} Wrong yandex token')
            return False

    # Проверка id ВК
    def check_vk_id(self):

        if len(self.vk_id) == 8:
            return True
        else:
            logging.error(f'{datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")} Wrong vk id')
            return False

    # Создание папки на Яндекс.Диске
    def create_folder_yandex_disk(self):
        self.date_time = datetime.datetime.now()
        self.prefix_folder_name = 'VK Photo Backup '
        self.postfix_folder_name = self.date_time.strftime('%d-%m-%y-%H-%M-%S')
        self.folder_name = self.prefix_folder_name + self.postfix_folder_name
        self.y.mkdir(self.folder_name)

    # Возвращает json с данными о фото профиля
    def get_vk_profile_photo(self):
        self.vk_params.update(
            {'owner_id': self.vk_id,
             'album_id': 'profile',
             'photo_sizes': 1,
             'extended': 1
             })
        try:
            requests.get(self._build_url('photos.get'), params=self.vk_params)
        except ConnectionError:
            return False

        response = requests.get(self._build_url('photos.get'), params=self.vk_params).json()
        return response['response']['items']

    # Загрузка фото на Яндекс.Диск
    def upload_photo_to_disk(self, count_photo=5):
        path_photo = self.get_vk_profile_photo()

        with open('info.json') as f:
            self.json_file = json.load(f)

        for photo_info in path_photo:
            str_date_time = datetime.datetime.fromtimestamp(photo_info['date']).strftime("%H-%M-%S_%d-%m-%y")

            for size in photo_info['sizes']:

                if self.photo_count != count_photo:

                    if size['type'] == 'x':
                        self.y.upload_url(size['url'],
                                          f'/{self.folder_name}/{str_date_time}')
                        self.photo_count += 1
                        self.json_data.update({'file_name': str_date_time, 'size': size['type']})
                        self.json_file.append(self.json_data)
                        # Отображение загрузки в логах:
                        # logging.info(f'{datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")} '
                        #              f'Photo "{str_date_time}" was uploaded in "{self.folder_name}"')

                        print(f'{self.photo_count} of {count_photo}')

        with open(f'info.json', 'w') as f:
            json.dump(self.json_file, f)


if __name__ == '__main__':

    if os.path.exists('info.json'):
        pass
    else:
        with open('info.json', 'w') as f:
            json.dump([], f)

    main = Main(VK_TOKEN, VK_ID, YANDEX_TOKEN)

    main.check_vk_token()
    main.check_yandex_token()
    main.check_vk_id()

    if main.check_vk_token() and main.check_yandex_token() and main.check_vk_id():
        main.create_folder_yandex_disk()
        main.upload_photo_to_disk()  # Введите в скобках кол-во фото для скачивания. По ум. - 5 фото.
    else:
        'Something wrong. See py_log.log'
