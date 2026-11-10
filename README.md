# Türkçe OCR Satır Verisi Üretici

OCR eğitimi için Türkçe satır görselleri ve metin etiketlerinden oluşan sentetik veri setleri üretir. Her satır ayrı bir PNG dosyasıdır; `labels.tsv` görseli doğru metinle eşler ve satırların belge içindeki okuma sırasını kaydeder.

## Kurulum

Python 3.9 veya üstü ve Türkçe karakterleri destekleyen bir yazı tipi gerekir.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Masaüstü uygulaması

```bash
.venv/bin/python app.py
```

macOS'ta paketlenmiş uygulama `dist/Türkçe OCR Satır Verisi Üretici.app` içindedir. Proje klasöründeki `Başlat.command` dosyası kaynak koddan arayüzü açar.

Arayüzden satır görseli sayısını, satır başına en az/en çok kelime sayısını, görsel ölçeğini, arka plan rengini, bozulma düzeyini, isteğe bağlı rastgelelik tohumunu ve çıktı ana klasörünü seçin. Türkçe destekli bir `.ttf` veya `.otf` yazı tipi seçebilirsiniz. Yazı tipi seçmezseniz sistemde bulunan uygun yazı tiplerinden biri kullanılır.

Her üretim, seçilen ana klasörün altında benzersiz bir `turkce_ocr_YYYYMMDD_HHMMSS` klasörü oluşturur. Önceki veri setlerinin üzerine yazılmaz.

## Komut satırı

```bash
.venv/bin/python satir_uret.py ./veri --ornek 1000 --min-kelime 4 --max-kelime 10 --olcek 1.5 --arka-plan krem --bozulma orta --tohum 42
```

Parametreler:

- `çıktı`: Yeni veri seti klasörlerinin oluşturulacağı ana klasör.
- `--ornek`: Üretilecek satır görseli sayısı (varsayılan 100).
- `--min-kelime`: Satır başına en az kelime (varsayılan 4).
- `--max-kelime`: Satır başına en çok kelime (varsayılan 9; üst sınır 30).
- `--tohum`: Aynı içerik ve görsel çeşitliliğini aynı ortamda yeniden üretmek için isteğe bağlı tam sayı.
- `--font`: Türkçe karakterleri destekleyen `.ttf` veya `.otf` dosyası.
- `--olcek`: Görsel boyutu ölçeği: `1`, `1.5` veya `2` (varsayılan `1`).
- `--arka-plan`: `beyaz`, `krem` veya `gri` (varsayılan `beyaz`).
- `--bozulma`: `az`, `orta` veya `yuksek` düzeyinde hafif dönüş, kontrast, bulanıklık ve görüntü gürültüsü (varsayılan `orta`).

Özel yazı tipiyle örnek:

```bash
.venv/bin/python satir_uret.py ./veri --ornek 500 --font ./fonts/DejaVuSans.ttf
```

## Çıktı yapısı

```text
turkce_ocr_20261110_120000/
├── labels.tsv
└── images/
    ├── doc0001_page0001_line0001.png
    └── ...
```

`labels.tsv`, UTF-8 kodlamalı ve sekmeyle ayrılmıştır. Sütunları:

| Sütun | Açıklama |
| --- | --- |
| `belge_id` | Sentetik belge kimliği |
| `sayfa` | Belge içindeki sayfa numarası; her 25 satırda artar |
| `satir` | Sayfa içindeki 1 tabanlı satır sırası |
| `dosya` | Veri seti klasörüne göreli PNG yolu |
| `metin` | Görselde yer alan satırın tam metni |

Aynı `belge_id` ve `sayfa` değerindeki satırlar `satir` alanına göre sıralanarak yeniden birleştirilebilir. Her PNG tek bir satır içerir; seçilen görsel ölçeği, arka plan rengi ve bozulma düzeyi üretime uygulanır. Veri sentetiktir ve OCR modelini eğitmez; görüntü ve etiket örnekleri sağlar.

## Uygulama paketi

Paketleme işlemini hedef işletim sisteminde çalıştırın.

macOS: `sh build_macos.sh`  
Windows Komut İstemi: `build_windows.bat`
