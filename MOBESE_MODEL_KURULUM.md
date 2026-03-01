# Mobese Özel Model Kurulumu

Mobese Seyret özelliği için **tamamen ayrı, optimize edilmiş modeller** kullanılır. Bu modeller mevcut modellerden bağımsızdır ve daha hızlı çalışır.

## Model Dosyaları

Mobese için özel modeller şu klasörlerde aranır:

### Araç Tespiti Modeli
- **Klasör**: `data/mobese-detector/`
- **Dosyalar**:
  - `mobese-vehicle.weights` - Model ağırlıkları
  - `mobese-vehicle.cfg` - Model konfigürasyonu
  - `mobese-vehicle.data` - Model veri dosyası

### Plaka Tespiti Modeli
- **Klasör**: `data/mobese-detector/`
- **Dosyalar**:
  - `mobese-lp-detector.h5` - Keras model dosyası

## Kurulum

### Seçenek 1: Hazır Modelleri İndir

Eğer hazır mobese modelleriniz varsa:

```bash
mkdir -p data/mobese-detector
# Modellerinizi bu klasöre kopyalayın
```

### Seçenek 2: Fallback Modu

Eğer mobese modelleri yoksa, sistem otomatik olarak normal modelleri optimize edilmiş şekilde kullanır:
- Normal araç tespiti modeli (düşük threshold ile)
- Normal plaka tespiti modeli (küçük input size ile)

## Model Özellikleri

Mobese modelleri şu özelliklere sahip olmalıdır:

1. **Hız**: Normal modellerden 3-5x daha hızlı
2. **Doğruluk**: Yüksek tespit oranı
3. **Hafif**: Daha küçük model boyutu
4. **Optimize**: Real-time işleme için optimize edilmiş

## Önerilen Modeller

Mobese için önerilen model türleri:

### Araç Tespiti
- YOLOv5n (nano) - Çok hızlı, hafif
- YOLOv8n (nano) - En yeni, optimize
- MobileNet-SSD - Mobil cihazlar için optimize

### Plaka Tespiti
- Lite WPOD-NET - Hafif versiyon
- MobileNet tabanlı plaka tespiti
- Özel eğitilmiş hafif model

## Test

Modelleri test etmek için:

```bash
python mobese-detection.py test_input/ test_output/
python mobese-lp-detection.py test_output/ dummy
```

## Notlar

- Mobese modelleri yoksa sistem normal modelleri kullanır (optimize edilmiş)
- Model dosyaları doğru klasörde olmalıdır
- Model formatları mevcut sistemle uyumlu olmalıdır

