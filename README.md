# simple-audio-cutter
Easy audio slicing solution for preparing a dataset for RVC or So-VITS-SVC
The essence of the program is that you specify a folder with audio files in any format (mp3, wav, flac) and convert them to multiple files with the chunk you specify.
This program uses multithreading, so it should greatly speed up the slicing of large datasets.

# Setup
1) Make sure you have [python](https://www.python.org/downloads/release/python-3109/)
2) Download programm [directly](https://github.com/daswer123/simple-audio-cutter/archive/refs/heads/main.zip) or via `git clone https://github.com/daswer123/simple-audio-cutter/`
3) Launch `run.bat`

This uses ffmpeg if you don't have it, the program will automatically install it in the program folder
If you do not specify an output folder, it will create an out folder inside the source folder

![image](https://github.com/daswer123/simple-audio-cutter/assets/22278673/853039e4-bb68-4747-9cfb-621f33fa629e)
