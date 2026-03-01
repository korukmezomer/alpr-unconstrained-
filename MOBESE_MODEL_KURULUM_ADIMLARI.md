# Mobese Model Kurulum Adımları

## 🎯 Önerilen: YOLOv4-tiny Kurulumu

YOLOv4-tiny, YOLOv3-tiny'den daha iyi doğruluk sunar ve hala çok hızlıdır.

### Adım 1: Model Dosyalarını İndir

```bash
cd "/Users/omerkorukmez/Desktop/yazılım mühendisliğinde gelişmeler 3/alpr-unconstrained/data/mobese-detector"

# YOLOv4-tiny weights indir
wget https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights -O mobese-vehicle.weights

# YOLOv4-tiny config indir
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg -O mobese-vehicle.cfg
```

### Adım 2: Mevcut Dosyaları Yedekle (İsteğe Bağlı)

```bash
# Mevcut YOLOv3-tiny'yi yedekle
mv mobese-vehicle.weights mobese-vehicle-yolov3-tiny.weights.backup
mv mobese-vehicle.cfg mobese-vehicle-yolov3-tiny.cfg.backup
```

### Adım 3: Test Et

```bash
cd "/Users/omerkorukmez/Desktop/yazılım mühendisliğinde gelişmeler 3/alpr-unconstrained"

# Test görüntüsü ile
mkdir -p test_mobese_input
mkdir -p test_mobese_output
# Bir test görüntüsü koyun test_mobese_input/ klasörüne

python mobese-detection.py test_mobese_input/ test_mobese_output/
```

## 🔧 Threshold Ayarlama

Model indirdikten sonra threshold'u ayarlayın:

```bash
# mobese-detection.py dosyasını düzenleyin
# vehicle_threshold = .25  # Varsayılan
# vehicle_threshold = .2   # Daha fazla tespit (daha düşük = daha fazla tespit)
```

## 📊 Model Performans Karşılaştırması

| Model | Araç Tespiti | Plaka Tespiti | Hız |
|-------|--------------|---------------|-----|
| YOLOv3-tiny (Mevcut) | ⭐⭐ | ⭐⭐ | ⚡⚡⚡ |
| YOLOv4-tiny (Önerilen) | ⭐⭐⭐ | ⭐⭐⭐ | ⚡⚡ |

## ⚠️ Sorun Giderme

### Model yüklenemiyor
- Dosya yollarını kontrol edin
- Darknet'in derlendiğinden emin olun: `cd darknet && make`

### Tespit yapılamıyor
- Threshold'u düşürün (0.2 veya 0.15)
- Görüntü kalitesini kontrol edin
- Model dosyalarının doğru olduğundan emin olun

### Çok yavaş
- YOLOv4-tiny yerine YOLOv3-tiny kullanın
- Frame skip'i artırın (15 → 20)

