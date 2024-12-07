import datetime
import json
import os
import time
import requests
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")


class VKTOYandex:
    VK_TOKEN = config['Tokens']['vk_token']
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, vk_id, ya_token):  # класс принимает вк айди и токен яндекса
        self.vk_id = vk_id
        self.ya_token = ya_token

    def get_common_params(self):
        return {
            'access_token': self.VK_TOKEN,
            'v': '5.199'
        }

    def _build_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'

    def get_photos_from_profile_vk(self):
        params = self.get_common_params()
        params.update({'owner_id': self.vk_id, 'album_id': 'profile', 'extended': 1})
        response = requests.get(self._build_url('photos.get'), params=params)
        photos_amount = response.json()['response']['count']
        types = []
        likes = []
        url = []
        file_names = []

        for i in response.json()["response"]['items']:
            likes.append(i['likes']['count'])  # добавляем в список лайки
            url.append(i["sizes"][-1]['url'])  # добавляем в список урлы
            types.append(i["sizes"][-1]['type'])  # добавляем в список размеры

        for count, j in enumerate(url):
            current_like = likes[count]
            if likes.count(current_like) == 1:  # если не дубль лайков, то просто кол-во лайков
                file_name = str(likes[count])
            else:  # а если дубль, то лайки + дата\время
                file_name = f'{likes[count]}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
            file_names.append(file_name)
            file_path = os.path.normpath(os.path.join
                                         (r"C:\Users\ksynj\IdeaProjects\Netology HW basic diploma\vk_photos",
                                          f"{file_name}.jpg"))
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):  # проверка, что папка существует, иначе будет создана
                print('1')
                os.makedirs(dir_path)
            with open(file_path, 'wb') as f:
                f.write(requests.get(j).content)
                print(f'Прогресс выполнения задачи: {(count + 1) / photos_amount * 100} процентов')
                time.sleep(3)  # слип нужен тк иначе не всегда успевает загрузиться фото

        names_types = {'name': "", "size": ""}  # создание файла с данными фото
        name_type_list = []
        for z in range(photos_amount):
            names_types['name'] = file_names[z]
            names_types["size"] = types[z]
            name_type_list.append(names_types.copy())
        with open('log.json', 'a') as log_file:
            log_file.write(json.dumps(name_type_list))

    def upload_photos_to_yadisk(self):
        folder = 'photo_from_vk'
        headers = {
            'Authorization': self.ya_token
        }
        params_create = {
            'path': folder
        }
        response_exist = requests.get('https://cloud-api.yandex.net/v1/disk/resources?path=photo_from_vk',
                                      headers=headers, params=params_create)
        if response_exist.status_code != 200 and response_exist.json()['error'] == "DiskNotFoundError":
            requests.put(f'https://cloud-api.yandex.net/v1/disk/resources?path={folder}',
                         headers=headers, params=params_create)

        root_dir = r'C:\Users\ksynj\IdeaProjects\Netology HW basic diploma\vk_photos'
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                params_upload = {'path': f'{folder}/{file}'}
                response_upload = requests.get(f'https://cloud-api.yandex.net/v1/disk/resources/upload',
                                               params=params_upload, headers=headers)
                with open(os.path.join(root, file), 'rb') as f:
                    requests.put(response_upload.json()['href'], files={'file': f})


if __name__ == '__main__':
    vk_client = VKTOYandex(28945641, config['Tokens']['ya_token'])
    vk_client.get_photos_from_profile_vk()
    vk_client.upload_photos_to_yadisk()
