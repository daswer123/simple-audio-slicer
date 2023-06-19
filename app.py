import os
import tkinter as tk
import ffmpeg
import asyncio
import concurrent.futures
import multiprocessing

from tkinter import filedialog
from queue import Queue
from threading import Thread
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed

class AudioCutterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simple Audio Cutter")

        self.input_label = tk.Label(master, text="Select the folder with the audio files: (wav, mp3, flac)")
        self.input_label.grid(row=0, column=0)

        self.input_entry = tk.Entry(master)
        self.input_entry.grid(row=0, column=1)

        self.input_button = tk.Button(master, text="Select...", command=self.choose_input_folder)
        self.input_button.grid(row=0, column=2)

        self.output_label = tk.Label(master, text="Select a folder to save: (Optional)")
        self.output_label.grid(row=1, column=0)

        self.output_entry = tk.Entry(master)
        self.output_entry.grid(row=1, column=1)

        self.output_button = tk.Button(master, text="Select...", command=self.choose_output_folder)
        self.output_button.grid(row=1, column=2)

        self.duration_label = tk.Label(master, text="Chunk duration (sec):")
        self.duration_label.grid(row=2, column=0)

        self.duration_scale = tk.Scale(master, from_=1, to=60, orient=tk.HORIZONTAL, command=self.update_duration)
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

        self.start_button = tk.Button(master, text="Start", command=self.start_cutting_thread)
        self.start_button.grid(row=6, column=0, columnspan=3)

        # Добавьте флажки для опций нормализации и затухания звука
        self.normalize_var = tk.BooleanVar()
        self.normalize_check = tk.Checkbutton(master, text="Normalize audio", variable=self.normalize_var)
        self.normalize_check.grid(row=4, column=0, columnspan=1)

        self.fade_var = tk.BooleanVar()
        self.fade_check = tk.Checkbutton(master, text="Fade in/out", variable=self.fade_var)
        self.fade_check.grid(row=4, column=1, columnspan=2)

    async def process_file(self, input_folder, output_folder, output_format):
        while not self.queue.empty():
            file = self.queue.get()
    
            file_path = os.path.join(input_folder, file)
            try:
                audio_duration = float(ffmpeg.probe(file_path)["format"]["duration"])
                num_cuts = int(audio_duration // self.duration)  
                if audio_duration % self.duration > 0:
                    num_cuts += 1
                for i in range(num_cuts):
                    start_time = i * self.duration
                    output_file = os.path.splitext(file)[0] + f"_cut_{i+1}.{output_format}"
                    output_file_path = os.path.join(output_folder, output_file)
    
                    loop = asyncio.get_event_loop()
                    audio = ffmpeg.input(file_path, ss=start_time, t=self.duration)

                    if self.normalize_var.get():
                        audio = audio.filter('loudnorm')

                    if self.fade_var.get():
                        audio = audio.filter('afade', type='in', start_time=0, duration=1).filter('afade', type='out', start_time=self.duration - 1, duration=1)

                    with ProcessPoolExecutor() as pool:
                        await loop.run_in_executor(pool, audio.output(output_file_path, threads=multiprocessing.cpu_count()).global_args('-y').run)

                    self.progress_label.config(text=f"Processed by {file} ({i+1}/{num_cuts})", fg="orange")
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

    def start_cutting_thread(self):
        self.thread = Thread(target=self.start_cutting)
        self.thread.start()

    def start_cutting(self):
        self.progress_label.config(text="Processing...", fg="black")
        input_folder = self.input_entry.get()
        output_folder = self.output_entry.get()
        output_format = self.format_var.get()

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
        asyncio.run(self.process_files(input_folder, output_folder, output_format))

    async def process_files(self, input_folder, output_folder, output_format):
        num_threads = multiprocessing.cpu_count()  # Определение числа потоков, равного количеству ядер процессора

        tasks = []  # Список задач для асинхронного выполнения
        for _ in range(num_threads):
            tasks.append(self.process_file(input_folder, output_folder, output_format))

        # Запуск всех задач асинхронно и ожидание их завершения
        await asyncio.gather(*tasks)

        self.progress_label.config(text="Done!", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    gui = AudioCutterGUI(root)
    root.mainloop()