#!/bin/sh
cd "$(dirname "$0")"
printf 'Türkçe OCR Satır Verisi Üretici başlatılıyor…\n'
exec .venv/bin/python app.py
