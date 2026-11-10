#!/usr/bin/env python3
"""Türkçe OCR eğitimi için satır görselleri ve TSV etiketleri üret."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
except ImportError as exc:
    print("Pillow bulunamadı. 'python3 -m pip install -r requirements.txt' çalıştırın. " + str(exc), file=sys.stderr)
    raise SystemExit(2) from exc


WORDS = """açık ağustos akış alan alışveriş amaç ana analiz anlaşma anket araç aralık artış aşama atama ay bilgi biçim birim belge bölge bütçe çalışma çağrı çevre çizelge çoklu değerlendirme değişiklik değer düzen duyuru eğitim ekip ekim ekran erişim eşgüdüm eşik faaliyet farklı görüş güven günlük hafta hizmet ihtiyaç ilişki işlem istatistik izleme içeriği karar kayıt kalite kapsam kaynak karşılaştırma katılım kâğıt koşul kontrol kurum kurul kullanımı kuyruk liste maliyet merkez mesaj mevzuat miktar müdürlük müşteri numara nisan ocak oda ölçüm örnek onay oran ortak görev gösterge plan program proje rapor sonuç süreç sayı saha salı sanayi sayfa sebep seçki seçenek seri servis sistem sözleşme süre şubat şube tablo tarih taslak taşınır teknik teklif temmuz temsilci tespit toplantı tutanak tür türkiye uygulama ulaşım uygunluk veri verim yöntem yönetim yetki yıl yürütme zaman""".split()

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Verdana.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/verdana.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]

LABEL_FIELDS = ["belge_id", "sayfa", "satir", "dosya", "metin"]
LINES_PER_PAGE = 25
BACKGROUND_COLORS = {
    "beyaz": (255, 255, 255),
    "krem": (250, 248, 240),
    "gri": (242, 244, 246),
}
DISTORTION_LEVELS = {
    "az": (0.25, 0.25, 0.15, (0.96, 1.04), 0.08, (0.08, 0.15), 0.15, 0.015),
    "orta": (0.65, 0.6, 0.5, (0.88, 1.08), 0.25, (0.1, 0.25), 0.35, 0.04),
    "yuksek": (0.85, 1.2, 0.7, (0.78, 1.15), 0.4, (0.12, 0.4), 0.6, 0.07),
}
IMAGE_SCALES = (1.0, 1.5, 2.0)


def _available_fonts(requested: Optional[str] = None):
    candidates = [requested] if requested else FONT_CANDIDATES
    available = []
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            ImageFont.truetype(candidate, size=36)
        except OSError:
            continue
        available.append(candidate)
    if not available:
        if requested:
            raise RuntimeError("Seçilen yazı tipi açılamadı. Türkçe karakter destekli .ttf/.otf dosyası seçin.")
        raise RuntimeError("Türkçe destekli yazı tipi bulunamadı. --font ile .ttf/.otf dosyası belirtin.")
    return available


def _make_line_text(rng: random.Random, min_words: int, max_words: int) -> str:
    count = rng.randint(min_words, max_words)
    words = [rng.choice(WORDS) for _ in range(count)]
    if rng.random() < 0.35:
        first = words[0]
        words[0] = first[:1].translate(str.maketrans({"i": "İ", "ı": "I"})).upper() + first[1:]
    if rng.random() < 0.08:
        words[-1] += rng.choice([",", ".", ";", ":"])
    return " ".join(words)


def _render_line(text: str, rng: random.Random, fonts, image_scale: float, background: str, distortion: str) -> Image.Image:
    font_path = rng.choice(fonts)
    font_size = round(rng.randint(32, 46) * image_scale)
    font = ImageFont.truetype(font_path, size=font_size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1), "white"))
    left, top, right, bottom = probe.textbbox((0, 0), text, font=font)
    pad_x, pad_y = round(24 * image_scale), round(18 * image_scale)
    background_color = BACKGROUND_COLORS[background]
    image = Image.new("RGB", (right - left + 2 * pad_x, bottom - top + 2 * pad_y), background_color)
    draw = ImageDraw.Draw(image)
    draw.text((pad_x - left, pad_y - top), text, font=font, fill=(rng.randint(20, 55),) * 3)

    rotate_chance, angle, contrast_chance, contrast_range, blur_chance, blur_range, noise_chance, noise_alpha = DISTORTION_LEVELS[distortion]
    if rng.random() < rotate_chance:
        image = image.rotate(rng.uniform(-angle, angle), resample=Image.Resampling.BICUBIC, expand=True, fillcolor=background_color)
    if rng.random() < contrast_chance:
        image = ImageEnhance.Contrast(image).enhance(rng.uniform(*contrast_range))
    if rng.random() < blur_chance:
        image = image.filter(ImageFilter.GaussianBlur(radius=rng.uniform(*blur_range)))
    if rng.random() < noise_chance:
        noise = Image.effect_noise(image.size, 12 if distortion == "orta" else 18).convert("RGB")
        image = Image.blend(image, noise, noise_alpha)
    return image


def _new_run_directory(output_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    base = "turkce_ocr_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = output_root / base
    suffix = 2
    while True:
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            candidate = output_root / (base + "_%02d" % suffix)
            suffix += 1


def generate_dataset(
    output_root: Union[str, Path],
    examples: int = 100,
    min_words: int = 4,
    max_words: int = 9,
    seed: Optional[int] = None,
    font_path: Optional[str] = None,
    image_scale: float = 1.0,
    background: str = "beyaz",
    distortion: str = "orta",
) -> Tuple[Path, int]:
    """Write line PNGs and ordered labels into a new run folder."""
    if examples < 1:
        raise ValueError("Örnek sayısı en az 1 olmalı.")
    if min_words < 1 or max_words < min_words or max_words > 30:
        raise ValueError("Kelime aralığı 1–30 arasında olmalı ve en az değeri en çok değerini aşmamalı.")
    if image_scale not in IMAGE_SCALES:
        raise ValueError("Görsel ölçeği 1, 1.5 veya 2 olmalı.")
    if background not in BACKGROUND_COLORS:
        raise ValueError("Arka plan beyaz, krem veya gri olmalı.")
    if distortion not in DISTORTION_LEVELS:
        raise ValueError("Bozulma düzeyi az, orta veya yuksek olmalı.")

    fonts = _available_fonts(font_path)
    rng = random.Random(seed)
    run_dir = _new_run_directory(Path(output_root).expanduser().resolve())
    images_dir = run_dir / "images"
    images_dir.mkdir()
    labels_path = run_dir / "labels.tsv"

    with labels_path.open("w", encoding="utf-8", newline="") as labels_file:
        writer = csv.DictWriter(labels_file, fieldnames=LABEL_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for index in range(examples):
            page = index // LINES_PER_PAGE + 1
            line = index % LINES_PER_PAGE + 1
            text = _make_line_text(rng, min_words, max_words)
            filename = "doc0001_page%04d_line%04d.png" % (page, line)
            relative_path = Path("images") / filename
            _render_line(text, rng, fonts, image_scale, background, distortion).save(run_dir / relative_path, format="PNG")
            writer.writerow({
                "belge_id": "doc0001",
                "sayfa": page,
                "satir": line,
                "dosya": relative_path.as_posix(),
                "metin": text,
            })
    return run_dir, examples


def main():
    parser = argparse.ArgumentParser(description="Türkçe OCR eğitimi için satır PNG'leri ve TSV etiketleri üretir.")
    parser.add_argument("çıktı", type=Path, help="Veri seti klasörlerinin oluşturulacağı ana klasör")
    parser.add_argument("--ornek", type=int, default=100, help="Üretilecek satır görseli sayısı (varsayılan: 100)")
    parser.add_argument("--min-kelime", type=int, default=4, help="Satır başına en az kelime (varsayılan: 4)")
    parser.add_argument("--max-kelime", type=int, default=9, help="Satır başına en çok kelime (varsayılan: 9)")
    parser.add_argument("--tohum", type=int, help="Tekrarlanabilir rastgelelik için sayı")
    parser.add_argument("--font", help="Türkçe destekli .ttf/.otf yazı tipi dosyası")
    parser.add_argument("--olcek", type=float, choices=IMAGE_SCALES, default=1.0, help="Görsel ölçeği: 1, 1.5 veya 2 (varsayılan: 1)")
    parser.add_argument("--arka-plan", choices=BACKGROUND_COLORS, default="beyaz", help="Arka plan rengi: beyaz, krem veya gri")
    parser.add_argument("--bozulma", choices=DISTORTION_LEVELS, default="orta", help="Görsel bozulma düzeyi: az, orta veya yuksek")
    args = parser.parse_args()
    run_dir, total = generate_dataset(args.çıktı, args.ornek, args.min_kelime, args.max_kelime, args.tohum, args.font, args.olcek, args.arka_plan, args.bozulma)
    print("Oluşturuldu: %s (%d satır görseli, labels.tsv)" % (run_dir, total))


if __name__ == "__main__":
    main()
