# best.pt Dosyası Kullanım Kılavuzu

## ✅ best.pt İndirildi ve Kuruldu!

**Konum**: `data/mobese-detector/mobese-lp-yolov8.pt`

Bu model Türk plakaları için özel olarak eğitilmiş YOLOv8 modelidir ve çok yüksek doğruluk sunar.

## 📦 Gereksinimler

### Ultralytics YOLOv8 Kurulumu

```bash
# ⚠️ ÖNEMLİ: Ultralytics Python 3 gerektirir!
# Python 2 ortamında kurulamaz!

# Python 3 ortamında kurulum:
conda activate base  # veya alpr_py3
pip install ultralytics

# Kontrol:
python3 -c "from ultralytics import YOLO; print('✅ Kuruldu!')"
```

**Not**: Ultralytics YOLOv8 **sadece Python 3** ile çalışır. Python 2 ortamında kurulamaz. Sistem otomatik olarak WPOD-NET'e fallback yapar.

## 🔧 Kullanım

### Otomatik Kullanım

Sistem otomatik olarak `best.pt` modelini kullanmaya çalışır:

1. **YOLOv8 mevcut ise**: `mobese-lp-yolov8-detection.py` kullanılır (best.pt ile)
2. **YOLOv8 yoksa**: `mobese-lp-detection.py` kullanılır (WPOD-NET ile)

### Manuel Test

```bash
# Test görüntüsü ile
python mobese-lp-yolov8-detection.py test_input/ test_output/
```

## 📊 Model Performansı

**best.pt Model Metrikleri**:
- **Precision (P)**: 0.998 (Çok yüksek doğruluk)
- **Recall (R)**: 0.973 (Yüksek hatırlama)
- **mAP50**: 0.994 (Mükemmel)
- **Hız**: ~3ms inference (Çok hızlı)

## ⚠️ Önemli Notlar

### Python 2/3 Uyumluluğu

`best.pt` modeli PyTorch/Ultralytics gerektirir ve **sadece Python 3 ile çalışır**.

**Çözüm Seçenekleri**:

1. **Seçenek 1**: Python 3 ortamında çalıştırın
   ```bash
   conda activate base  # veya başka Python 3 ortamı
   pip install ultralytics
   python web_app.py
   ```

2. **Seçenek 2**: WPOD-NET kullanın (Python 2 uyumlu)
   - `mobese-lp-detection.py` zaten mevcut ve çalışıyor
   - YOLOv8 yoksa otomatik olarak WPOD-NET kullanılır

3. **Seçenek 3**: Hybrid yaklaşım
   - Araç tespiti: Python 2 (Darknet)
   - Plaka tespiti: Python 3 (YOLOv8) - ayrı script

## 🚀 Hızlı Başlangıç

### 1. Ultralytics YOLOv8 Kur

```bash
# Python 3 ortamında
pip install ultralytics
```

### 2. Model Dosyasını Kontrol Et

```bash
ls -lh data/mobese-detector/mobese-lp-yolov8.pt
```

### 3. Test Et

```bash
python mobese-lp-yolov8-detection.py test_input/ test_output/
```

## 🔄 Fallback Mekanizması

Sistem şu sırayla çalışır:

1. **YOLOv8 best.pt** (varsa ve ultralytics yüklüyse) → En iyi doğruluk
2. **WPOD-NET** (fallback) → Mevcut, çalışıyor

## 📝 Model Detayları

- **Model Tipi**: YOLOv8n (nano - hızlı)
- **Eğitim Verisi**: Türk plakaları (Roboflow dataset)
- **Format**: PyTorch (.pt)
- **Boyut**: ~6 MB
- **Doğruluk**: %99.4 mAP50

## 🔗 Kaynak

- **GitHub Repo**: https://github.com/Semihocakli/turkish-plate-recognition-w-yolov8-onnx-to-engine-cpp
- **Model Konumu**: `detection_weights/best.pt`
- **Alternatif**: `detection_weights/best.onnx` (ONNX formatında)

## 💡 İpuçları

1. **Python 3 gerekli**: Ultralytics Python 3 gerektirir
2. **GPU hızlandırma**: CUDA varsa otomatik kullanılır
3. **Confidence threshold**: Script'te 0.3 olarak ayarlı (değiştirilebilir)
4. **Fallback**: YOLOv8 yoksa WPOD-NET kullanılır (sorun yok)

