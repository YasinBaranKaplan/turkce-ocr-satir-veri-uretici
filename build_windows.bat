@echo off
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
python -m pip install pyinstaller
if errorlevel 1 exit /b 1
python -m PyInstaller --noconfirm --clean --windowed --onefile --name TurkceOCRSatirVeriUretici app.py
if errorlevel 1 exit /b 1
echo Uygulama: dist\TurkceOCRSatirVeriUretici.exe
