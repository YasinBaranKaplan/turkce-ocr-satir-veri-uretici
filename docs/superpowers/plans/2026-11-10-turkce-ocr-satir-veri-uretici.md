# Türkçe OCR Satır Verisi Üreticisi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mevcut PDF aracını Türkçe satır PNG'leri ve sıralı TSV etiketleri üreten masaüstü/CLI aracına dönüştürmek.

**Architecture:** `satir_uret.py` satır metinlerini, görüntülerini, çıktı klasörünü ve TSV'yi tek bir üretim akışında oluşturacak. Tkinter arayüzü bu ortak üretim fonksiyonunu arka plan iş parçacığında çağıracak; README ve paketleme adları yeni ürünü anlatacak.

**Tech Stack:** Python 3.9+, Tkinter, Pillow, argparse, `csv`/UTF-8 TSV.

**Spec:** `docs/superpowers/specs/2026-11-10-turkce-ocr-satir-veri-uretici-design.md`

## Global Constraints

- Mevcut Python, Tkinter ve Pillow yığını korunur.
- Etiket biçimi UTF-8 TSV'dir; başlıklar `belge_id`, `sayfa`, `satir`, `dosya`, `metin` olur.
- Her çalıştırma tek bir sentetik belge üretir; her 25 satırda yeni bir sayfa başlar.
- Örnek sayısı satır görüntüsü adedini belirler.
- Çıktı ana klasörü mevcutsa yeni, benzersiz bir alt klasör oluşturulur; önceki içeriklere dokunulmaz.
- İlk sürüm tek satır görüntüsü üretir, kelime kutusu/karakter koordinatı içermez.
- Gerçek kişi/kurum verisi kullanılmaz.

## Review Focus

Otomatik test ekleme veya çalıştırma bu görev kapsamında istenmediğinden bu planda test adımı yoktur. Uygulama sırasında README'de doğru CLI kullanımı ve GUI akışı açıklanmalıdır.

---

### Task 1: Satır görüntüsü veri üreticisi ve CLI

**Files:**
- Create: `satir_uret.py`
- Keep temporarily: `belge_uret.py` until the GUI switches to the new generator.

**Interfaces:**
- Produces: `generate_dataset(output_root, examples=100, min_words=4, max_words=9, seed=None, font_path=None, image_scale=1.0, background="beyaz", distortion="orta") -> (Path, int)`
- Produces CLI options: positional output root and `--ornek`, `--min-kelime`, `--max-kelime`, `--tohum`, `--font`, `--olcek`, `--arka-plan`, `--bozulma`.
- Output: unique run directory with `labels.tsv` and `images/doc0001_page0001_line0001.png`-style PNG paths; all paths in TSV are relative to the run directory.

- [x] **Step 1: Implement deterministic Turkish line text generation** in `satir_uret.py`; keep the vocabulary and names fictional, draw each selected line from exactly the words written to its label, and validate example/word bounds before creating output.
- [x] **Step 2: Implement row image rendering** in `satir_uret.py` with Turkish-capable font discovery, text-fitted PNG canvases, and selectable scale/background plus restrained rotation/contrast/noise/blur levels that preserve label text.
- [x] **Step 3: Implement unique run folder and ordered TSV metadata** in `generate_dataset`; create `labels.tsv` as UTF-8 with the exact five design headers, fixed `belge_id`, pages of 25 lines, 1-based line numbers per page, and deterministic file names.
- [x] **Step 4: Add the CLI** in `satir_uret.py`; map CLI arguments for examples, word bounds, seed, font, image scale, background, and distortion to `generate_dataset` and print the created run directory and number of line images.

### Task 2: Masaüstü arayüzünü satır veri setine dönüştürme

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `satir_uret.generate_dataset(output_root, examples, min_words, max_words, seed, font_path) -> (run_path, image_count)`.
- GUI fields: example count, minimum/maximum words per line, output root folder, optional seed/font, image scale, background, distortion level.

- [x] **Step 1: Replace PDF settings** in `GeneratorApp.__init__` and `_build` with the GUI fields above and Turkish copy describing line PNGs plus TSV labels.
- [x] **Step 2: Replace save-file selection** with output-folder selection and pass the root folder to the shared generator.
- [x] **Step 3: Update input validation and background worker** so count, word bounds, scale, background, and distortion are passed to the shared generator and the UI stays responsive while it runs.
- [x] **Step 4: Update completion and error states** to show the new run directory, generated image count, and any actionable font/output error.

### Task 3: Kurulum ve kullanım belgelerini güncelleme

**Files:**
- Modify: `README.md`
- Modify: `Başlat.command`
- Modify: `build_macos.sh`
- Modify: `build_windows.bat`
- Delete: `belge_uret.py`

- [x] **Step 1: Rewrite README** for line-image datasets, installation, GUI launch, CLI examples, TSV columns, 25-lines-per-page ordering, unique output folders, Turkish font support, seed behavior, image controls, and usage examples.
- [x] **Step 2: Update launcher and package labels** to call the updated GUI and use a Turkish OCR dataset producer name in the packaged app/executable.
- [x] **Step 3: Remove obsolete PDF claims and commands** from user-facing documentation and packaging output labels.
