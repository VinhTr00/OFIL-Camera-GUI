import requests
import os
import getpass

class DataDownload():
    def __init__(self, folder='OFIL', ip_addr='192.168.0.100'):
        self.url_picture = f'http://{ip_addr}/Pictures/'
        self.url_video = f'http://{ip_addr}/Videos/'
        self.response = requests.get(self.url)
        self.username = getpass.getuser()
        self.folder_path = f"/home/{self.username}/Downloads/{folder}"
        if not os.path.exists(self.folder_path):
            # Create the folder
            os.makedirs(self.folder_path)
            print(f"Folder '{self.folder_path}' created successfully.")
        else:
            print(f"Folder '{self.folder_path}' already exists.")
            
    def downloadPicture(self, name_picture):
        destination_path = self.url_picture + f'{name_picture}' + ".jpg"
        if self.response.status_code == 200:
            with open(destination_path, 'wb') as file:
                file.writes(self.response.content)
            print('Picture downloaded successfully.')
        else:
            print(f'Error downloading picture. Status code: {self.response.status_code}')
        
        
    def downloadVideo(self, name_video):
        destination_path = self.url_video + f'{name_video}' + ".mov"
        if self.response.status_code == 200:
            with open(destination_path, 'wb') as file:
                file.writes(self.response.content)
            print('Picture downloaded successfully.')
        else:
            print(f'Error downloading picture. Status code: {self.response.status_code}')