# simple-audio-slicer
Easy audio slicing solution for preparing a dataset for RVC or So-VITS-SVC
The essence of the program is that you specify a folder with audio files in any format (mp3, wav, flac) and convert them to multiple files with the chunk you specify.
This program uses multithreading, so it should greatly speed up the slicing of large datasets.

Check the [video demonstration](https://github.com/daswer123/simple-audio-slicer#demo)

# Setup
# 1 - Pre-build
1) Just dowload [exe file](https://github.com/daswer123/simple-audio-slicer/releases/download/0.5/Simple.Audio.Slicer.exe)
    
# 2 - Manuly 
1) Make sure you have [python](https://www.python.org/downloads/release/python-3109/)
2) Download programm [directly](https://github.com/daswer123/simple-audio-cutter/archive/refs/heads/main.zip) or via `git clone https://github.com/daswer123/simple-audio-cutter/`
3) Launch `run.bat`

This uses ffmpeg if you don't have it, the program will automatically install it in the program folder

If you do not specify an output folder, it will create an out folder inside the source folder

![image](https://github.com/daswer123/simple-audio-slicer/assets/22278673/684ba839-8fc7-4c84-98fd-417164972704)

**Convert audio to mono** 

**Normalize**

Normalizes all output chunks

# Demo

https://github.com/daswer123/simple-audio-slicer/assets/22278673/1df1c3fc-4eb8-4342-a694-20c83affa96c

