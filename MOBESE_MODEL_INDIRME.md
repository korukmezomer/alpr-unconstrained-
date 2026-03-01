# Mobese için Önerilen Modeller - GitHub Linkleri

Mobese kısmında daha iyi çalışması için önerilen modeller ve indirme linkleri.

## 🚗 Araç Tespiti Modelleri

### 1. YOLOv5 Nano (ÖNERİLEN - Çok Hızlı)
**GitHub**: https://github.com/ultralytics/yolov5
**Model**: YOLOv5n (nano - en hızlı)
**İndirme**:
```bash
# YOLOv5n weights (6.4 MB - çok hızlı)
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt -O data/mobese-detector/mobese-vehicle-yolov5n.pt
```

**Not**: Bu PyTorch formatında. Darknet'e çevirmek gerekebilir veya PyTorch script'i yazılabilir.

### 2. YOLOv3-tiny (MEVCUT - Darknet Formatında)
**Durum**: ✅ Zaten indirildi
**Konum**: `data/mobese-detector/mobese-vehicle.weights`
**Kaynak**: https://pjreddie.com/darknet/yolo/

### 3. YOLOv4-tiny (Daha İyi Doğruluk)
**GitHub**: https://github.com/AlexeyAB/darknet
**İndirme**:
```bash
# YOLOv4-tiny weights (23 MB)
wget https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights -O data/mobese-detector/mobese-vehicle-yolov4-tiny.weights
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg -O data/mobese-detector/mobese-vehicle-yolov4-tiny.cfg
```

**Avantaj**: YOLOv3-tiny'den daha iyi doğruluk, hala hızlı.

### 4. YOLOv8 Nano (En Yeni - ÖNERİLEN)
**GitHub**: https://github.com/ultralytics/ultralytics
**Model**: YOLOv8n (nano)
**İndirme**:
```bash
# YOLOv8n weights (6.2 MB)
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt -O data/mobese-detector/mobese-vehicle-yolov8n.pt
```

**Not**: PyTorch formatında, dönüştürme gerekebilir.

## 🔢 Plaka Tespiti Modelleri

### 1. WPOD-NET (MEVCUT)
**Durum**: ✅ Zaten var
**Konum**: `data/mobese-detector/mobese-lp-detector.h5`

### 2. YOLOv8 License Plate Detection (✅ İNDİRİLDİ - ÖNERİLEN)
**GitHub**: https://github.com/Semihocakli/turkish-plate-recognition-w-yolov8-onnx-to-engine-cpp
**Model**: Türk plakaları için özel eğitilmiş
**Durum**: ✅ İndirildi ve kuruldu
**Konum**: `data/mobese-detector/mobese-lp-yolov8.pt`
**Performans**: 
- Precision: 0.998 (Çok yüksek)
- Recall: 0.973
- mAP50: 0.994
- Hız: ~3ms inference

**Kurulum**:
```bash
# Repo'yu klonlayın
git clone https://github.com/Semihocakli/turkish-plate-recognition-w-yolov8-onnx-to-engine-cpp.git

# best.pt dosyasını kopyalayın
cp turkish-plate-recognition-w-yolov8-onnx-to-engine-cpp/detection_weights/best.pt data/mobese-detector/mobese-lp-yolov8.pt

# Ultralytics YOLOv8 kurun (Python 3 gerekli)
pip install ultralytics
```

**Not**: Bu model Python 3 gerektirir. Python 2 ile çalışmaz. Sistem otomatik olarak YOLOv8 varsa kullanır, yoksa WPOD-NET'e fallback yapar.

### 3. EasyOCR + YOLO Plaka Tespiti
**GitHub**: https://github.com/JaidedAI/EasyOCR
**Model**: Önceden eğitilmiş OCR modeli
**Kurulum**:
```bash
pip install easyocr
```

### 4. OpenALPR (Alternatif)
**GitHub**: https://github.com/openalpr/openalpr
**Not**: C++ tabanlı, Python wrapper'ı var

## 📦 Hızlı Kurulum - Önerilen Kombinasyon

### Seçenek 1: YOLOv4-tiny + WPOD-NET (ÖNERİLEN)
```bash
cd data/mobese-detector

# YOLOv4-tiny indir (daha iyi doğruluk)
wget https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights -O mobese-vehicle.weights
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg -O mobese-vehicle.cfg

# COCO data dosyası (zaten var)
# mobese-vehicle.data ve mobese-vehicle.names zaten mevcut
```

### Seçenek 2: Mevcut YOLOv3-tiny + İyileştirilmiş Threshold
Mevcut modeli kullanarak threshold'u daha da düşürebilirsiniz:
- `mobese-detection.py` içinde threshold: 0.25 → 0.2

## 🔧 Model Entegrasyonu

### Darknet Formatı (Mevcut Sistem)
1. `.weights` dosyasını `data/mobese-detector/` klasörüne koyun
2. `.cfg` dosyasını `data/mobese-detector/` klasörüne koyun
3. `mobese-vehicle.data` dosyasını güncelleyin (gerekirse)
4. `mobese-detection.py` otomatik olarak kullanacak

### PyTorch Formatı (.pt)
PyTorch modelleri için ayrı bir script gerekir veya ONNX'e çevrilip kullanılabilir.

## 📊 Model Karşılaştırması

| Model | Hız | Doğruluk | Boyut | Format |
|-------|-----|----------|-------|--------|
| YOLOv3-tiny | ⚡⚡⚡ | ⭐⭐ | 34 MB | Darknet |
| YOLOv4-tiny | ⚡⚡ | ⭐⭐⭐ | 23 MB | Darknet |
| YOLOv5n | ⚡⚡⚡ | ⭐⭐⭐ | 6.4 MB | PyTorch |
| YOLOv8n | ⚡⚡⚡ | ⭐⭐⭐⭐ | 6.2 MB | PyTorch |

## 🚀 Hızlı Test

Modeli indirdikten sonra test edin:

```bash
# Test görüntüsü ile
python mobese-detection.py test_input/ test_output/
```

## 📝 Notlar

1. **YOLOv4-tiny önerilir**: YOLOv3-tiny'den daha iyi doğruluk, hala çok hızlı
2. **Threshold ayarı**: Model indirdikten sonra threshold'u 0.2-0.25 arası deneyin
3. **COCO dataset**: YOLOv3-tiny ve YOLOv4-tiny COCO üzerinde eğitilmiş (car, bus, truck içerir)
4. **Plaka modeli**: WPOD-NET mevcut, alternatif olarak YOLOv8 tabanlı modeller deneyebilirsiniz

## 🔗 Faydalı Linkler

- **YOLOv5**: https://github.com/ultralytics/yolov5
- **YOLOv8**: https://github.com/ultralytics/ultralytics
- **Darknet**: https://github.com/AlexeyAB/darknet
- **OpenALPR**: https://github.com/openalpr/openalpr
- **Turkish Plate Recognition**: https://github.com/Semihocakli/turkish-plate-recognition-w-yolov8-onnx-to-engine-cpp

