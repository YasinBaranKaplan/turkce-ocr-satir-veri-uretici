#!/bin/sh
set -eu
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --clean --windowed --name "Sentetik OCR Belge Üretici" app.py
printf '\nUygulama: dist/Sentetik OCR Belge Üretici.app\n'
