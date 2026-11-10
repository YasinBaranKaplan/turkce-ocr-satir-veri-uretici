# Sentetik OCR Belge Üretici

Türkçe içerikli, kurgusal kurumsal sayfa düzenlerinde 1–10 sayfalı PDF üretir. Her sayfa tek bir JPEG görüntüsü olarak PDF'ye eklenir; PDF'de seçilebilir metin katmanı bulunmaz.

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

Mac'te hazır uygulama `dist/Sentetik OCR Belge Üretici.app` içindedir. Proje klasöründeki `Başlat.command` dosyası kaynak koddan arayüzü açar.

Arayüzden sayfa sayısını, sayfa başına 0–2 tabloyu, sayfa gövdesindeki kelime sayısını (40–400), çözünürlüğü, isteğe bağlı rastgelelik tohumunu ve PDF'nin kaydedileceği yeri seçebilirsiniz. Tablo sayısını 0 yapmak tabloları kaldırır; 1 veya 2 yapmak tablo ekler. Kelime sayısı, her sayfanın gövdesine yazılan sentetik Türkçe kelime adedidir.

## Komut satırı

```bash
.venv/bin/python belge_uret.py cikti.pdf
.venv/bin/python belge_uret.py cikti.pdf --sayfa 5 --tablolar 2 --kelime 280 --dpi 220 --tohum 42
```

Sayfa sayısı verilmezse rastgele 1–10 arasında seçilir. `--tablolar` sayfa başına tablo adedini (0–2), `--kelime` gövde metnindeki kelime adedini (40–400) belirler. `--font` ile yazı tipi dosyası belirtilebilir. Aynı tohum, aynı içeriği yeniden üretir.

## Uygulama paketi

Paketleme işlemini hedef işletim sisteminde çalıştırın.

macOS: `sh build_macos.sh`  
Windows Komut İstemi: `build_windows.bat`

Belge ve kurum adları kurgusaldır. Gerçek kurum amblemi, mühür veya imza kullanılmaz; sayfalarda sentetik test ibaresi bulunur.
