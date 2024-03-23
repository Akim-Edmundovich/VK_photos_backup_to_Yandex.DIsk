import time
import requests
import datetime  # import datetime
import yadisk
import json
from settings import VK_TOKEN, VK_ID, YANDEX_TOKEN


class VKAPIClient:  # Создаю класс, который может взаимодействовать с данными пользователя из ВК
    '''Класс, являющийся клиентом к API VK '''

    API_BASE_URL = 'https://api.vk.com/method'  # Базовый URL

    def __init__(self, token, user_id) -> None:
        self.token = token
        self.user_id = user_id
        self.params = {
            'access_token': self.token,  # Token
            'v': '5.131'  # Версия VK
        }
        self.file_info_list = []

    def _build_url(self, api_metod):  # Метод с 1 параметром, возвращающий базовый URL + параметр
        return f'{self.API_BASE_URL}/{api_metod}'

    def check_token(self):
        response = requests.get(self._build_url('users.get'),
                                params=self.params).json()

        if 'error' in response.keys():
            return '---Incorrect VK token!---'
            # print(response['response'][0]['id']) #'Incorrect token!'
        elif response['response'][0]['id']:
            print('VK token is correct!')
            return True

    def get_profile_photo(self):  # Метод получает информацию о фото профиля пользователя

        self.params.update(
            {'owner_id': self.user_id,  # Дополняю словарь с общ. парам. ID пользователя и ID альбома с фото
             'album_id': 'profile',
             'photo_sizes': 1,
             'extended': 1
             })
        response = requests.get(self._build_url('photos.get'),
                                params=self.params).json()

        return response  # Возвращаю данные из запроса


class Yandex:
    count = 0  # счетик для остановки копирования фото
    json_data = []

    def __init__(self, token):
        self.token = token
        self.y = yadisk.YaDisk(token=token)
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    # Проверка токена Яндекс
    def check_token(self):
        if self.y.check_token():
            print('Yandex token is correct!')
            return True
        else:
            print('---Incorrect Yandex token!---')
            return False

    # Создание папки в Я.Диске после проверки токена
    def create_folder(self):
        '''Проверка токена Яндекс и создание папки'''
        self.date_time = datetime.datetime.now()
        self.prefix_folder_name = 'VK Photo Backup '
        self.postfix_folder_name = self.date_time.strftime('%d-%m-%y-%H-%M-%S')

        if self.y.check_token():  # Если токен яндекс валидный:
            self.folder_name = self.prefix_folder_name + self.postfix_folder_name
            self.y.mkdir(self.folder_name)
        else:
            print('!!! INVALID TOKEN !!!')

    # Загрузка на диск
    def upload_to_disk(self, count_photo=5):
        '''Загрузка на диск'''
        self.count_photo = count_photo

        json_photo = vk.get_profile_photo()  # Получение данных о фото в json-формате
        path_photo = json_photo['response']['items']  # Переходит к нужному месту в json

        print('Progress:')

        with open('info.json') as f:
            self.json_file = json.load(f)

        for i in path_photo:  # Вывод нужного URL и даты-времени в string
            dt = datetime.datetime.fromtimestamp(i['date'])  # Перевод метки времени в читабельный формат даты_времени
            str_date_time = dt.strftime("%d_%m_%Y_%H_%M_%S")  # Форматирование времени-даты для имени фото

            for s in i['sizes']:  # Проход циклом по спискам в ['sizes']
                if self.count != self.count_photo:  # Если счетчик не равен счетчику по умолчанию/введенному пользователем
                    if s['type'] == 'x':
                        self.y.upload_url(s['url'],
                                          f'/{self.folder_name}/{str_date_time}')  # Загружает фото на диск и именует "дата_время"
                        self.count += 1  # Добавляет к счетчику +1
                        file_info = {'file_name': str_date_time, 'size': s['type']}  # Словарь с данными о фото
                        self.json_file.append(file_info)

                        print(f'Photo "{str_date_time}" was uploaded in "{self.folder_name}"', end='\n')

        with open('info.json', 'w') as f:
            json.dump(self.json_file, f)

        print('Success!')


if __name__ == '__main__':

    print('Hello! Your backup APP is ready')
    time.sleep(0.5)

    vk_token = VK_TOKEN
    vk_id = VK_ID
    vk = VKAPIClient(vk_token, vk_id)

    yandex_token = YANDEX_TOKEN
    yandex = Yandex(yandex_token)

    print('Checking VK token...')
    time.sleep(0.5)
    if vk.check_token() == True:
        vk.get_profile_photo()
        time.sleep(0.5)
        print('Checking Yandex token...')
        time.sleep(0.5)

        if yandex.check_token() == True:
            time.sleep(0.5)
            photo_count = input('How many photos do you want to copy(default 5)?\nPress "Enter" to skip:\n')
            yandex.create_folder()

            if photo_count:
                yandex.upload_to_disk(int(photo_count))
            else:
                yandex.upload_to_disk()


        else:
            time.sleep(0.5)
            print('Try again.')
    else:
        time.sleep(0.5)
        print('Try again.')
