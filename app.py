import os
import tkinter as tk
import asyncio
import concurrent.futures
import shutil
import multiprocessing
import time

from tkinter import filedialog
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

def download_ffmpeg():
    import requests
    import zipfile

    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2023-06-19-14-02/ffmpeg-N-111159-g1617d1a752-win64-lgpl-shared.zip"
    filename = "ffmpeg.zip"

    response = requests.get(url)
    response.raise_for_status()

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

import subprocess

def check_ffmpeg():
    def ffmpeg_is_installed():
        try:
            result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result)
            if "ffmpeg version" in result.stdout:
                return True
        except FileNotFoundError:
            return False
        return False

    if not ffmpeg_is_installed():
        print("FFmpeg not found. Checking the local installation...")
        if os.path.exists("ffmpeg\\bin\\ffmpeg.exe"):
            print("FFmpeg found locally.")
        else:
            print("Downloading and installing FFmpeg...")
            os.makedirs("ffmpeg")
            download_ffmpeg()
        os.environ["PATH"] = os.path.abspath("ffmpeg\\bin") + os.pathsep + os.environ["PATH"]
    else:
        print("FFmpeg found.")


import ffmpeg

class AudioCutterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simple Audio Slicer")

        self.input_label = tk.Label(master, text="Select the folder with the audio files: (wav, mp3, flac)")
        self.input_label.grid(row=0, column=0)

        self.input_entry = tk.Entry(master)
        self.input_entry.grid(row=0, column=1)

        self.input_button = tk.Button(master, text="Select...", command=self.choose_input_folder)
        self.input_button.grid(row=0, column=2)

        self.output_label = tk.Label(master, text="Select a output folder: (Optional)")
        self.output_label.grid(row=1, column=0)

        self.output_entry = tk.Entry(master)
        self.output_entry.grid(row=1, column=1)

        self.output_button = tk.Button(master, text="Select...", command=self.choose_output_folder)
        self.output_button.grid(row=1, column=2)

        self.duration_label = tk.Label(master, text="Chunk duration (sec): , If you set 0, you just tranfer transoform files")
        self.duration_label.grid(row=2, column=0)

        self.duration_scale = tk.Scale(master, from_=0, to=60, orient=tk.HORIZONTAL, command=self.update_duration)
        self.duration_scale.set(10)
        self.duration_scale.grid(row=2, column=1)

        self.format_label = tk.Label(master, text="Select the format of the output files:")
        self.format_label.grid(row=3, column=0)

        self.format_var = tk.StringVar(master)
        self.format_var.set("wav")

        self.mp3_radio = tk.Radiobutton(master, text="MP3 (slow)", variable=self.format_var, value="mp3")
        self.mp3_radio.grid(row=3, column=2)

        self.wav_radio = tk.Radiobutton(master, text="WAV", variable=self.format_var, value="wav")
        self.wav_radio.grid(row=3, column=1)

        self.progress_label = tk.Label(master, text="Waiting...")
        self.progress_label.grid(row=5, column=0, columnspan=3)

        self.progress_queue = asyncio.Queue()
        self.processed_files = 0

        self.start_button = tk.Button(master, text="Start", command=self.start_double_pass_thread)
        self.start_button.grid(row=6, column=0, columnspan=3)

        # Add checkboxes for sound normalization and attenuation options
        self.normalize_var = tk.BooleanVar()
        self.normalize_check = tk.Checkbutton(master, text="Normalize audio", variable=self.normalize_var)
        self.normalize_check.grid(row=4, column=0, columnspan=1)

        self.cut_large_files = tk.BooleanVar()
        self.cut_large_files_check = tk.Checkbutton(master, text="Cut large files (> 2 min)", variable=self.cut_large_files)
        self.cut_large_files_check.grid(row=4, column=1, columnspan=2)

        self.convert_mono = tk.BooleanVar()
        self.convert_mono_check = tk.Checkbutton(master, text="Convert all files to mono", variable=self.convert_mono)
        self.convert_mono_check.grid(row=5, column=1, columnspan=2)

    async def process_file(self, input_folder, output_folder, output_format, duration):
     while not self.queue.empty():
         file = self.queue.get()

         file_path = os.path.join(input_folder, file)
         try:
             audio_duration = float(ffmpeg.probe(file_path)["format"]["duration"])

             if duration == 0:
                 num_cuts = 1
             else:
                 num_cuts = int(audio_duration // duration)
                 if audio_duration % duration > 0:
                     num_cuts += 1

             for i in range(num_cuts):
                 start_time = i * duration if duration > 0 else 0
                 output_file = os.path.splitext(file)[0]
                 output_file += f"_cut_{i+1}" if duration > 0 else ""
                 output_file += f".{output_format}"
                 output_file_path = os.path.join(output_folder, output_file)

                 loop = asyncio.get_event_loop()
                 audio = ffmpeg.input(file_path, ss=start_time)

                 if duration > 0:
                     audio = ffmpeg.input(file_path, ss=start_time, t=duration)

                 if self.normalize_var.get():
                     audio = audio.filter('loudnorm')

                 if self.cut_large_files.get():
                     print("slice large files")
                    #  audio = audio.filter('afade', type='in', start_time=0, duration=1).filter('afade', type='out', start_time=duration - 1, duration=1)

                 if self.convert_mono.get():
                    output_args = {
                        'threads': multiprocessing.cpu_count(),
                        'ac': 1,
                        'y': None
                    }
                 else:
                     output_args = {
                        'threads': multiprocessing.cpu_count(),
                        'y': None
                    }

                 with ThreadPoolExecutor() as pool:
                     await loop.run_in_executor(pool, audio.output(output_file_path, **output_args).run)

                #  self.progress_label.config(text=f"Processed by {file} ({i+1}/{num_cuts})", fg="orange")
                 self.processed_files += 1
                 self.progress_label.config(text=f"Processed {self.processed_files}/{self.queue.qsize() + self.processed_files} files", fg="orange")
         except Exception as e:
            print(f"File processing error {file}: {e}")

    def choose_input_folder(self):
        folder = filedialog.askdirectory()
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, folder)

    def choose_output_folder(self):
        folder = filedialog.askdirectory()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, folder)

    def update_duration(self, value):
        self.duration = int(value)

    def start_double_pass_thread(self):
        self.double_pass_thread = Thread(target=self.double_pass_cutting)
        self.double_pass_thread.start()

    def double_pass_cutting(self):
        # Сохраняем текущее значение нарезки
        original_duration = self.duration
        original_input_folder = self.input_entry.get()
        original_output_folder = self.output_entry.get()
        output_format = self.format_var.get()

        # Создаем временную папку
        temp_folder = os.path.join(original_input_folder, "temp")
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # Первый этап: нарезка по 1 минуте
            if self.cut_large_files.get():
              first_cut_future = executor.submit(self.start_cutting, 60, original_input_folder, temp_folder, output_format)
              first_cut_future.result()  # Ожидаем завершение первого этапа

            if not original_output_folder:
                original_output_folder = os.path.join(original_input_folder, "out")
                os.makedirs(original_output_folder, exist_ok=True)

            # Второй этап: нарезка на указанное время
            if self.cut_large_files.get():
                second_cut_future = executor.submit(self.start_cutting, original_duration, temp_folder, original_output_folder, output_format)
                second_cut_future.result()  # Ожидаем завершение второго этапа
            else: 
                second_cut_future = executor.submit(self.start_cutting, original_duration, original_input_folder, original_output_folder, output_format)
                second_cut_future.result()  # Ожидаем завершение второго этапа
        

        shutil.rmtree(temp_folder)


    def start_cutting_thread(self):
        duration = self.duration
        input_folder = self.input_entry.get()
        output_folder = self.output_entry.get()
        output_format = self.format_var.get()
        self.thread = Thread(target=self.start_cutting, args=(duration, input_folder, output_folder, output_format))
        self.thread.start()

    def start_cutting(self, duration, input_folder, output_folder, output_format):
        self.progress_label.config(text="Processing...", fg="black")

        if not output_folder:
            output_folder = os.path.join(input_folder, "out")
            os.makedirs(output_folder, exist_ok=True)

        # Создайте очередь и добавьте файлы
        self.queue = Queue()
        for file in os.listdir(input_folder):
            file_path = os.path.join(input_folder, file)
            if os.path.isfile(file_path):
                self.queue.put(file)

        # Запуск обработки файлов асинхронно
        asyncio.run(self.process_files(input_folder, output_folder, output_format,duration))

    async def process_files(self, input_folder, output_folder, output_format,duration):
        num_threads = multiprocessing.cpu_count()  # Определение числа потоков, равного количеству ядер процессора

        tasks = []  # Список задач для асинхронного выполнения
        for _ in range(num_threads):
            tasks.append(self.process_file(input_folder, output_folder, output_format,duration))

        # Запуск всех задач асинхронно и ожидание их завершения
        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()
        elapsed_time = end_time - start_time

        self.processed_files = 0
        self.progress_label.config(text=f"Done! Processing took {elapsed_time:.2f} seconds", fg="green")        

if __name__ == "__main__":
    check_ffmpeg()  
    root = tk.Tk()
    gui = AudioCutterGUI(root)
    root.mainloop()