#!/bin/sh
set -eu
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --clean --windowed --name "Türkçe OCR Satır Verisi Üretici" app.py
printf '\nUygulama: dist/Türkçe OCR Satır Verisi Üretici.app\n'
