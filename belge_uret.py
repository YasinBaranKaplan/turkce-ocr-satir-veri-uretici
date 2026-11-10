#!/usr/bin/env python3
"""Türkçe, görüntü tabanlı sentetik OCR PDF'leri üret."""

from __future__ import annotations

import argparse
import io
import random
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
except ImportError as exc:
    print("Pillow bulunamadı. 'python3 -m pip install -r requirements.txt' çalıştırın. " + str(exc), file=sys.stderr)
    raise SystemExit(2) from exc

PAGE_W_MM, PAGE_H_MM = 210, 297
WORDS = """açık ağustos akış alan alışveriş amaç ana analiz anlaşma anket araç aralık artış aşama atama ay bilgi biçim birim belge bölge bütçe çalışma çağrı çevre çizelge çoklu değerlendirme değişiklik değer düzen duyuru eğitim ekip ekim ekran erişim eşgüdüm eşik faaliyet farklı görüş güven günlük hafta hizmet ihtiyaç ilişki işlem istatistik izleme içeriği karar kayıt kalite kapsam kaynak karşılaştırma katılım kâğıt koşul kontrol kurum kurul kullanımı kuyruk liste maliyet merkez mesaj mevzuat miktar müdürlük müşteri numara nisan ocak oda ölçüm örnek onay oran ortak görev gösterge plan program proje rapor sonuç süreç sayı saha salı sanayi sayfa sebep seçki seçenek seri servis sistem sözleşme süre şubat şube tablo tarih taslak taşınır teknik teklif temmuz temsilci tespit toplantı tutanak tür türkiye uygulama ulaşım uygunluk veri verim yöntem yönetim yetki yıl yürütme zaman""".split()
NAMES = ["Aylin Yılmaz", "Çağrı Şahin", "İpek Özdemir", "Mert Kılıç", "Şule Aydın", "Yağız Demir", "Öykü Çetin", "Eylül Koç", "Özgür Arslan", "Gökçe Kurt"]
UNITS = ["Kuzey Bölge Koordinasyon Birimi", "Kent Hizmetleri Araştırma Merkezi", "Maviçınar Kurumsal İşler Müdürlüğü", "Örnekova Planlama ve İzleme Dairesi", "Yeniyol Destek Hizmetleri Birimi", "Günışığı Veri ve Değerlendirme Kurulu"]
SUBJECTS = ["Yıllık çalışma planı", "Birimler arası bilgi paylaşımı", "Hizmet süreçlerinin değerlendirilmesi", "Başvuru kayıtlarının güncellenmesi", "Dönemsel faaliyet özeti", "Kurumsal kaynak çizelgesi", "Saha çalışması sonuçları", "Toplantı kararlarının izlenmesi"]
LOCATIONS = ["Aydınlık", "Çamlıbel", "Güneykent", "Kavaklı", "Marmara", "Yeniköy", "Örnekova", "Pınarbaşı"]
STATUS = ["Tamamlandı", "İncelemede", "Planlandı", "Beklemede", "Uygun", "Güncellendi"]


def load_font(size, requested=None, bold=False):
    paths = [requested] if requested else []
    if bold:
        paths += ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Verdana Bold.ttf", "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    paths += [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Verdana.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in paths:
        if path and Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    raise RuntimeError("Türkçe destekli yazı tipi bulunamadı. --font ile .ttf/.otf dosyası belirtin.")


def sentence(rng, low=9, high=21):
    words = " ".join(rng.choice(WORDS) for _ in range(rng.randint(low, high)))
    return words[0].upper() + words[1:] + "."


def worded_paragraphs(rng, word_count):
    """Generate body paragraphs containing exactly word_count vocabulary words."""
    paragraphs = []
    remaining = word_count
    while remaining:
        paragraph_sentences = []
        paragraph_size = 0
        while remaining and paragraph_size < 100:
            sentence_size = min(remaining, rng.randint(10, 17))
            sentence_words = [rng.choice(WORDS) for _ in range(sentence_size)]
            sentence_words[0] = sentence_words[0].capitalize()
            paragraph_sentences.append(" ".join(sentence_words) + ".")
            remaining -= sentence_size
            paragraph_size += sentence_size
        paragraphs.append(" ".join(paragraph_sentences))
    return paragraphs


def wrap(draw, text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def paragraph(draw, text, x, y, width, font, scale):
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, fill=(55, 55, 55), font=font)
        y += font.size + round(8 * scale)
    return y


def header(draw, rng, fonts, page_no, total, scale, width):
    margin = round(145 * scale)
    dark, gray = (40, 54, 68), (105, 115, 122)
    lw = max(1, round(2 * scale))
    draw.rectangle((margin, round(125*scale), margin+round(54*scale), round(179*scale)), outline=dark, width=lw)
    draw.line((margin+round(11*scale), round(152*scale), margin+round(43*scale), round(152*scale)), fill=dark, width=lw)
    draw.line((margin+round(27*scale), round(136*scale), margin+round(27*scale), round(168*scale)), fill=dark, width=lw)
    draw.text((margin+round(72*scale), round(122*scale)), rng.choice(UNITS), font=fonts["bold"], fill=dark)
    draw.text((margin+round(72*scale), round(158*scale)), "KURUMSAL YAZIŞMA VE KAYIT", font=fonts["tiny"], fill=gray)
    draw.text((width-margin-round(250*scale), round(132*scale)), f"Belge: {rng.randint(1000,9999)}-{rng.randint(10,99)}", font=fonts["tiny"], fill=gray)
    draw.line((margin, round(202*scale), width-margin, round(202*scale)), fill=(140,145,148), width=lw)
    stamp = (date(2021,1,1) + timedelta(days=rng.randint(0,1800))).strftime("%d.%m.%Y")
    draw.text((margin, round(217*scale)), f"Kayıt tarihi: {stamp}", font=fonts["tiny"], fill=gray)
    draw.text((width-margin-round(170*scale), round(217*scale)), f"Sayfa {page_no} / {total}", font=fonts["tiny"], fill=gray)
    draw.text((width-margin-round(310*scale), round(169*scale)), "SENTETİK OCR ÖRNEĞİ", font=fonts["tiny"], fill=(130,130,130))
    return margin, width-margin


def draw_table(draw, rng, x, y, width, fonts, scale, count):
    widths = [int(width*.12), int(width*.33), int(width*.28), int(width*.27)]
    labels = ["Sıra", "Birim / konu", "Durum", "Açıklama"]
    row_h, pad = round(45*scale), round(8*scale)
    x_positions = [x]
    for col_w in widths:
        x_positions.append(x_positions[-1] + col_w)
    for i, label in enumerate(labels):
        draw.rectangle((x_positions[i], y, x_positions[i+1], y+row_h), fill=(220,225,228), outline=(115,122,126), width=max(1,round(scale)))
        draw.text((x_positions[i]+pad, y+round(12*scale)), label, fill=(35,45,52), font=fonts["small"])
    y += row_h
    for n in range(1, count+1):
        vals = [f"{n:02}", rng.choice(LOCATIONS)+" "+rng.choice(["birimi","şubesi","ekibi"]), rng.choice(STATUS), " ".join(rng.choice(WORDS) for _ in range(3)).capitalize()]
        for i, value in enumerate(vals):
            draw.rectangle((x_positions[i], y, x_positions[i+1], y+row_h), fill=(250,250,248) if n%2 else (241,243,243), outline=(150,154,156), width=max(1,round(scale)))
            font = fonts["tiny"] if len(value)>16 else fonts["small"]
            for j, line in enumerate(wrap(draw, value, font, widths[i]-2*pad)[:2]):
                draw.text((x_positions[i]+pad, y+round(7*scale)+j*round(19*scale)), line, fill=(55,55,55), font=font)
        y += row_h
    return y


def make_page(rng, page_no, total, dpi, tables_per_page, words_per_page, font_path):
    width, height = round(PAGE_W_MM/25.4*dpi), round(PAGE_H_MM/25.4*dpi)
    scale = dpi/180
    image = Image.new("RGB", (width,height), (247,246,242))
    draw = ImageDraw.Draw(image)
    fonts = {
        "title": load_font(round(34*scale), font_path, True),
        "body": load_font(round((19 if words_per_page <= 220 else 17 if words_per_page <= 320 else 16)*scale), font_path),
        "small": load_font(round(16*scale), font_path),
        "bold": load_font(round(17*scale), font_path, True),
        "tiny": load_font(round(13*scale), font_path),
    }
    margin, right = header(draw, rng, fonts, page_no, total, scale, width)
    y = round(300*scale)
    kind = rng.choice(["yazı", "form", "rapor", "toplantı", "çizelge"])
    draw.text((margin,y), rng.choice(SUBJECTS).upper(), font=fonts["title"], fill=(35,45,55))
    y += round(62*scale)

    if kind == "form":
        fields = [("Başvuru sahibi",rng.choice(NAMES)), ("Kayıt konusu"," ".join(rng.choice(WORDS) for _ in range(4)).capitalize()), ("İlgili birim",rng.choice(UNITS)), ("İşlem durumu",rng.choice(STATUS)), ("Açıklama",sentence(rng,5,9))]
        for label,value in fields:
            fh = round(58*scale)
            draw.rounded_rectangle((margin,y,right,y+fh), radius=round(5*scale), outline=(145,151,155), width=max(1,round(scale)))
            draw.text((margin+round(14*scale),y+round(5*scale)), label, font=fonts["tiny"], fill=(110,115,118))
            draw.text((margin+round(14*scale),y+round(25*scale)), value, font=fonts["small"], fill=(45,48,50))
            y += round(70*scale)
    else:
        draw.text((margin,y), f"Konu: {rng.choice(SUBJECTS)}    İlgi: {rng.choice(UNITS)}", font=fonts["bold"], fill=(67,77,83))
        y += round(45*scale)
    for para in worded_paragraphs(rng, words_per_page):
        y = paragraph(draw, para, margin, y, right-margin, fonts["body"], scale) + round(14*scale)

    for table_no in range(tables_per_page):
        label = "İZLEME ÇİZELGESİ" if tables_per_page == 1 else f"EK ÇİZELGE {table_no+1}"
        draw.text((margin,y), label, font=fonts["bold"], fill=(45,55,62))
        y += round(25*scale)
        y = draw_table(draw,rng,margin,y,right-margin,fonts,scale,rng.randint(2,3))
    footer_y = min(max(y+round(36*scale), height-round(300*scale)), height-round(200*scale))
    draw.line((margin,footer_y,right,footer_y), fill=(175,177,176), width=max(1,round(scale)))
    draw.text((margin,footer_y+round(14*scale)), "Hazırlayan: "+rng.choice(NAMES), font=fonts["small"], fill=(65,68,70))
    draw.text((right-round(430*scale),footer_y+round(14*scale)), "Kontrol: "+rng.choice(NAMES), font=fonts["small"], fill=(65,68,70))
    draw.text((margin,height-round(100*scale)), "Bu belge yalnızca OCR testleri için rastgele oluşturulmuştur.", font=fonts["tiny"], fill=(125,127,127))
    if rng.random()<.8:
        image = image.rotate(rng.uniform(-.45,.45), resample=Image.Resampling.BICUBIC, fillcolor=(239,238,234), expand=False)
    if rng.random()<.6:
        image = ImageEnhance.Contrast(image).enhance(rng.uniform(.82,1.05))
    return image.filter(ImageFilter.GaussianBlur(radius=rng.choice([0,0,.15,.25])))


def _stream(dictionary, data):
    return dictionary + b"\nstream\n" + data + b"\nendstream"


def _write_pdf(path, objects):
    data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, body in enumerate(objects[1:], 1):
        offsets.append(len(data))
        data.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        data.extend(body + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects)}\n".encode("ascii"))
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    path.write_bytes(data)


def generate_pdf(output, pages=None, tables_per_page=0, words_per_page=160, dpi=180, seed=None, font_path=None):
    if pages is not None and not 1 <= pages <= 10:
        raise ValueError("Sayfa sayısı 1 ile 10 arasında olmalı.")
    if not 0 <= tables_per_page <= 2:
        raise ValueError("Sayfa başına tablo sayısı 0 ile 2 arasında olmalı.")
    if not 40 <= words_per_page <= 400:
        raise ValueError("Sayfa başına kelime sayısı 40 ile 400 arasında olmalı.")
    if not 100 <= dpi <= 400:
        raise ValueError("DPI değeri 100 ile 400 arasında olmalı.")
    rng = random.Random(seed)
    total = pages or rng.randint(1,10)
    output = Path(output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    pw, ph = PAGE_W_MM/25.4*72, PAGE_H_MM/25.4*72
    objects = [b"",b"",b""]
    page_ids = []
    for page_no in range(1,total+1):
        image = make_page(rng,page_no,total,dpi,tables_per_page,words_per_page,font_path)
        jpeg = io.BytesIO()
        image.save(jpeg,format="JPEG",quality=88,optimize=True)
        raw = jpeg.getvalue()
        page_id = len(objects)
        content_id, image_id = page_id+1, page_id+2
        page_ids.append(page_id)
        content = f"q\n{pw:.3f} 0 0 {ph:.3f} 0 0 cm\n/Im0 Do\nQ\n".encode("ascii")
        page = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {pw:.3f} {ph:.3f}] "
                f"/Resources << /XObject << /Im0 {image_id} 0 R >> >> /Contents {content_id} 0 R >>").encode("ascii")
        objects.extend([
            page,
            _stream(f"<< /Length {len(content)} >>".encode("ascii"),content),
            _stream((f"<< /Type /XObject /Subtype /Image /Width {image.width} /Height {image.height} "
                     f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(raw)} >>").encode("ascii"),raw),
        ])
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {total} >>".encode("ascii")
    _write_pdf(output,objects)
    return output,total


def main():
    parser = argparse.ArgumentParser(description="Türkçe, görüntü tabanlı sentetik OCR PDF'i üretir.")
    parser.add_argument("çıktı", type=Path, help="Oluşturulacak PDF dosyasının yolu")
    parser.add_argument("--sayfa", type=int, choices=range(1,11), metavar="1-10", help="Sayfa sayısı (varsayılan: rastgele 1–10)")
    parser.add_argument("--tablolar", type=int, choices=range(0,3), default=0, help="Sayfa başına tablo sayısı: 0–2")
    parser.add_argument("--kelime", type=int, default=160, help="Sayfa gövdesindeki kelime sayısı: 40–400")
    parser.add_argument("--dpi", type=int, default=180, help="Raster çözünürlüğü, 100–400")
    parser.add_argument("--tohum", type=int, help="Tekrarlanabilir rastgelelik tohumu")
    parser.add_argument("--font", help="Türkçe destekli .ttf/.otf yazı tipi dosyası")
    args = parser.parse_args()
    output,total = generate_pdf(args.çıktı,args.sayfa,args.tablolar,args.kelime,args.dpi,args.tohum,args.font)
    print(f"Oluşturuldu: {output} ({total} sayfa, yalnızca taranmış görünt)")


if __name__ == "__main__":
    main()
