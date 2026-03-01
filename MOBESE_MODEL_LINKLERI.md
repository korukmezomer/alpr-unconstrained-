# 🚀 Mobese için Önerilen Modeller - GitHub Linkleri

## ✅ YOLOv4-tiny İndirildi!

YOLOv4-tiny modeli başarıyla indirildi ve kuruldu. Bu model YOLOv3-tiny'den daha iyi doğruluk sunar.

**Konum**: `data/mobese-detector/mobese-vehicle-yolov4-tiny.weights`

## 📦 Diğer Önerilen Modeller

### 1. Araç Tespiti Modelleri

#### YOLOv4-tiny (✅ İNDİRİLDİ - ÖNERİLEN)
- **GitHub**: https://github.com/AlexeyAB/darknet
- **Release**: https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights
- **Config**: https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
- **Boyut**: 23 MB
- **Performans**: YOLOv3-tiny'den %15-20 daha iyi doğruluk

#### YOLOv5 Nano (PyTorch - Dönüştürme Gerekir)
- **GitHub**: https://github.com/ultralytics/yolov5
- **Model**: YOLOv5n
- **İndirme**: https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt
- **Boyut**: 6.4 MB
- **Not**: PyTorch formatında, Darknet'e çevirmek gerekir

#### YOLOv8 Nano (PyTorch - Dönüştürme Gerekir)
- **GitHub**: https://github.com/ultralytics/ultralytics
- **Model**: YOLOv8n
- **İndirme**: https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
- **Boyut**: 6.2 MB
- **Not**: PyTorch formatında, en yeni model

### 2. Plaka Tespiti Modelleri

#### Turkish Plate Recognition (YOLOv8 - ÖNERİLEN)
- **GitHub**: https://github.com/Semihocakli/turkish-plate-recognition-w-yolov8-onnx-to-engine-cpp
- **Özellik**: Türk plakaları için özel eğitilmiş
- **Format**: ONNX/PyTorch
- **Not**: Repo'yu klonlayıp model dosyalarını kontrol edin

#### WPOD-NET (MEVCUT)
- **Durum**: ✅ Zaten var
- **Konum**: `data/mobese-detector/mobese-lp-detector.h5`

#### EasyOCR (Alternatif OCR)
- **GitHub**: https://github.com/JaidedAI/EasyOCR
- **Kurulum**: `pip install easyocr`
- **Özellik**: 80+ dil desteği, önceden eğitilmiş

## 🔧 Hızlı Kurulum

### YOLOv4-tiny Kullanımı (Zaten İndirildi)

Sistem otomatik olarak YOLOv4-tiny'yi kullanacak. Eğer kullanmıyorsa:

```bash
# YOLOv4-tiny'yi aktif et
cd data/mobese-detector
mv mobese-vehicle.weights mobese-vehicle-yolov3-tiny.weights.backup
mv mobese-vehicle.cfg mobese-vehicle-yolov3-tiny.cfg.backup
cp mobese-vehicle-yolov4-tiny.weights mobese-vehicle.weights
cp mobese-vehicle-yolov4-tiny.cfg mobese-vehicle.cfg
```

### Threshold Ayarlama

Daha fazla tespit için threshold'u düşürün:

```python
# mobese-detection.py içinde
vehicle_threshold = .15  # Çok agresif (daha fazla tespit, daha fazla false positive)
vehicle_threshold = .2   # Dengeli (önerilen)
vehicle_threshold = .25  # Konservatif (daha az tespit, daha az false positive)
```

## 📊 Model Performansı

| Model | Araç Tespiti | Hız | Boyut | Durum |
|-------|--------------|-----|-------|-------|
| YOLOv3-tiny | ⭐⭐ | ⚡⚡⚡ | 34 MB | ✅ Mevcut |
| YOLOv4-tiny | ⭐⭐⭐ | ⚡⚡ | 23 MB | ✅ İndirildi |
| YOLOv5n | ⭐⭐⭐ | ⚡⚡⚡ | 6.4 MB | ⚠️ PyTorch |
| YOLOv8n | ⭐⭐⭐⭐ | ⚡⚡⚡ | 6.2 MB | ⚠️ PyTorch |

## 🎯 Önerilen Kombinasyon

**Mobese için**: YOLOv4-tiny + WPOD-NET
- YOLOv4-tiny: Daha iyi araç tespiti
- WPOD-NET: Mevcut plaka tespiti (iyi çalışıyor)
- Threshold: 0.2 (dengeli)

## 🔗 Faydalı Linkler

1. **Darknet GitHub**: https://github.com/AlexeyAB/darknet
2. **YOLOv5 GitHub**: https://github.com/ultralytics/yolov5
3. **YOLOv8 GitHub**: https://github.com/ultralytics/ultralytics
4. **Turkish Plate Recognition**: https://github.com/Semihocakli/turkish-plate-recognition-w-yolov8-onnx-to-engine-cpp
5. **EasyOCR**: https://github.com/JaidedAI/EasyOCR
6. **OpenALPR**: https://github.com/openalpr/openalpr

## ⚠️ Sorun Giderme

### Model yüklenemiyor
- Dosya yollarını kontrol edin
- Darknet'in derlendiğinden emin olun
- Model dosyalarının tam olduğundan emin olun

### Hala tespit yapılamıyor
1. Threshold'u düşürün (0.2 → 0.15)
2. YOLOv4-tiny kullandığınızdan emin olun
3. Görüntü kalitesini kontrol edin
4. Console log'larını kontrol edin

### Çok yavaş
- YOLOv4-tiny yerine YOLOv3-tiny kullanın
- Frame skip'i artırın (15 → 20)

