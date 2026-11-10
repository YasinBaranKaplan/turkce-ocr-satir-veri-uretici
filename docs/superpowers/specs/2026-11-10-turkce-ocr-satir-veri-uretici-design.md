# Türkçe OCR Satır Verisi Üreticisi

## Niyet

Mevcut sentetik Türkçe PDF üreticisini, satır görüntüleri ve bunların doğru metin etiketlerinden oluşan OCR eğitim veri setleri üreten bir masaüstü aracı ve komut satırı programına dönüştürmek. Model tek satırdaki Türkçe kelimeleri okuyabilmeli; etiketlerdeki sıra bilgisi satırların tekrar birleştirilerek belge metnine dönüştürülmesini sağlamalı.

## Hedefler

- Her eğitim örneği için Türkçe karakterleri destekleyen PNG satır görseli üretmek.
- Her görseli tam satır metni, belge/sayfa kimliği ve satır sırasıyla TSV etiket dosyasına bağlamak.
- Örnek sayısını, satır başına kelime aralığını, görüntü özelliklerini ve rastgelelik tohumunu ayarlamak.
- Masaüstü arayüzü ve komut satırından aynı üretim mantığını kullanmak.
- Yazı tipi, hafif dönüş, gürültü ve kontrast gibi kontrollü görsel çeşitlilik sağlamak; etiket metnini görüntüye gerçekten çizilen metinden üretmek.

## Hedef dışı

- Kelime kutuları veya karakter düzeyinde sınır koordinatları üretmek.
- OCR modelini eğitmek ya da değerlendirmek.
- Belge sayfası düzeni, sütunlar veya karmaşık tablo satırı tespiti üretmek.
- Gerçek kişi/kurum verisi kullanmak.

## Başarı ölçütleri

- Çıktı dizinindeki her TSV satırı geçerli bir PNG dosyasına karşılık gelir.
- `belge_id`, `sayfa`, `satir`, `dosya`, `metin` alanları ile aynı belge sayfalarının satırları okuma sırasıyla birleştirilebilir.
- Sabit tohum aynı ortam ve yazı tipiyle aynı örnek metinlerini ve sıralamasını üretir.
- Türkçe `ç, ğ, ı, İ, ö, ş, ü` karakterleri etiketlerde ve uygun yazı tiplerinde doğru korunur.

## Yaklaşımlar

1. **Satır görselleri + etiketler (seçilen):** Her satır ayrı PNG, eşleşen TSV metni ve sıra bilgisi. Satır OCR'ına doğrudan eğitim verir ve okuma sırasını veri üstverisiyle korur.
2. **Kelime görselleri + etiketler:** Kelime tanımayı öğretir ancak satır bağlamını ve satır birleştirmeyi kapsamaz.
3. **Tam sayfa + satır kutuları:** Daha gerçekçi sayfa girdisi sağlar fakat satır tespiti koordinatları gerektirir ve ilk sürümün kapsamını büyütür.

Seçilen yaklaşım, kullanıcının kelimeleri satırlarda tanıma ve satırları birleştirme hedefiyle en doğrudan eşleşendir.

## Ürün davranışı

- Her üretim, kullanıcının seçtiği çıktı ana klasörünün altında çakışma yapmayan yeni bir veri seti klasöründe görseller ve bir `labels.tsv` dosyası oluşturur. Var olan üretimleri değiştirmez.
- Dosya adları çakışmayacak şekilde belge, sayfa ve satır numarası içerir.
- Örnek sayısı oluşturulacak satır görseli adedidir. Satırlar bir belge içinde sayfalara sıralı olarak bölünür; varsayılan olarak sayfa başına 25 satır, son sayfada daha az satır olabilir.
- TSV içindeki kimlik ve sıra alanları satırların yeniden birleştirilmesine yeter.
- GUI örnek sayısını, satır başına en az/en çok kelimeyi, çıktı ana klasörünü ve isteğe bağlı tohumu sunar; üretim sırasında arayüz yanıt vermeye devam eder ve tamamlanma/hatayı bildirir.
- CLI aynı ayarları seçeneklerle sunar ve varsayılanları README'de belgeler.
- Mevcut PDF odaklı kontroller ve açıklamalar satır veri seti akışına göre yenilenir; PDF üretimi temel çıktı olarak kalmaz.

## Kısıtlar ve uygulama kararları

- Mevcut Python, Tkinter ve Pillow yığını korunur.
- Etiket biçimi UTF-8 TSV'dir; başlıklar `belge_id`, `sayfa`, `satir`, `dosya`, `metin` olur.
- Her çalıştırma tek bir sentetik belge üretir; her 25 satırda yeni bir sayfa başlar.
- Örnek sayısı satır görüntüsü adedini belirler.
- Çıktı ana klasörü mevcutsa yeni, benzersiz bir alt klasör oluşturulur; önceki içeriklere dokunulmaz.
- Görsel adı deterministik kimliklerden türetilir; içerik metni ve satır sırası tohumla üretilebilir.
- İlk sürüm tek satır görüntüsü üretir, kelime kutusu/karakter koordinatı içermez.
- Görsel boyutu, yazı tipi, arka plan ve bozulma düzeyi kullanıcıya sunulacak minimum anlaşılır ayarlarla seçilir; gereksiz ayar kalabalığından kaçınılır.

## Açık kararları uygulayıcı belirleyebilir

- Uygun varsayılan çözünürlük ve kelime aralığı.
- Kapsamı dar tutan yazı tipi ve bozulma çeşitliliği.
- CLI seçenek adları ve arayüzdeki alan yerleşimi.
- Eski PDF üretim kodunun kaldırılması mı yoksa erişilemeyen yardımcı kod olarak tutulması mı gerektiği; kullanıcı arayüzü ve ana dokümantasyon yeni veri seti akışını anlatmalıdır.
