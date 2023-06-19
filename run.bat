@echo off
chcp 65001

echo Creating a virtual environment...
python -m venv venv

echo Activating a virtual environment...
call venv\Scripts\activate

echo Setting Dependencies...
pip install -r requirements.txt

echo Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo FFmpeg not found. Checking the local installation...
    if exist ffmpeg\bin\ffmpeg.exe (
        echo FFmpeg найден локально.
    ) else (
        echo Downloading and installing FFmpeg...
        mkdir ffmpeg
        python download_ffmpeg.py
    )
    set "PATH=%CD%\ffmpeg\bin;%PATH%"
) else (
    echo FFmpeg found.
)

echo Running the application...
python app.py

echo Deactivating the virtual environment...
call venv\Scripts\deactivate.bat

echo Completion of work...
timeout /t 3 /nobreak >nul