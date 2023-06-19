import requests
import zipfile
import os
import shutil

url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2023-06-19-14-02/ffmpeg-N-111159-g1617d1a752-win64-lgpl-shared.zip"
filename = "ffmpeg.zip"

response = requests.get(url)
with open(filename, 'wb') as f:
    f.write(response.content)

with zipfile.ZipFile(filename, 'r') as zip_ref:
    # Извлекаем содержимое архива во временную папку
    temp_folder = "temp_ffmpeg"
    zip_ref.extractall(temp_folder)

os.remove(filename)

# Перемещаем содержимое папки ffmpeg-N-111159-g1617d1a752-win64-lgpl-shared в папку ffmpeg
source_folder = os.path.join(temp_folder, "ffmpeg-N-111159-g1617d1a752-win64-lgpl-shared")

for item in os.listdir(source_folder):
    source = os.path.join(source_folder, item)
    destination = os.path.join("ffmpeg", item)
    if os.path.isdir(source):
        if os.path.exists(destination):
            # Если папка уже существует, объединяем содержимое
            for subitem in os.listdir(source):
                os.rename(os.path.join(source, subitem), os.path.join(destination, subitem))
        else:
            os.rename(source, destination)
    else:
        os.rename(source, destination)

# Удаляем временную папку
shutil.rmtree(temp_folder)