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
start /b /wait cmd /c python app.py

echo Terminating any remaining app.py processes...
for /f "tokens=2" %%i in ('tasklist /nh /fi "imagename eq python.exe"') do taskkill /pid %%i /f >nul 2>&1

echo Deactivating the virtual environment...
call venv\Scripts\deactivate.bat

echo Completion of work...
timeout /t 1 /nobreak >nul