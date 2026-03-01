# Ultralytics YOLOv8 Kurulum Kılavuzu

## ⚠️ Önemli: Python 3 Gerektirir

`ultralytics` kütüphanesi **sadece Python 3** ile çalışır. Python 2 ortamında kurulamaz.

## 🔧 Kurulum Seçenekleri

### Seçenek 1: Base (Python 3) Ortamında Kurulum (ÖNERİLEN)

```bash
# Base ortamına geç
conda activate base

# Ultralytics'i kur
pip install ultralytics

# Kontrol et
python -c "from ultralytics import YOLO; print('Ultralytics kuruldu!')"
```

### Seçenek 2: Yeni Python 3 Ortamı Oluştur

```bash
# Yeni Python 3 ortamı oluştur
conda create -n alpr_py3 python=3.8 -y
conda activate alpr_py3

# Ultralytics'i kur
pip install ultralytics

# Kontrol et
python -c "from ultralytics import YOLO; print('Ultralytics kuruldu!')"
```

### Seçenek 3: Python 2'de Çalışmaya Devam Et (WPOD-NET)

Eğer Python 3 kurmak istemiyorsanız:
- Sistem otomatik olarak **WPOD-NET** kullanacak
- `best.pt` modeli kullanılmayacak
- Mevcut sistem çalışmaya devam edecek

## 🚀 Sistem Nasıl Çalışır?

Sistem **otomatik fallback** mekanizmasına sahip:

1. **Python 3 + Ultralytics varsa** → `best.pt` (YOLOv8) kullanılır ✅
2. **Python 3 yoksa veya Ultralytics yoksa** → WPOD-NET kullanılır ✅

**Her iki durumda da sistem çalışır!**

## 📋 Kontrol Komutları

### Python 3 Kontrolü
```bash
python3 --version
# Python 3.x.x olmalı
```

### Ultralytics Kontrolü
```bash
python3 -c "from ultralytics import YOLO; print('Ultralytics mevcut!')"
```

### Model Dosyası Kontrolü
```bash
ls -lh data/mobese-detector/mobese-lp-yolov8.pt
# 6.0 MB olmalı
```

## 🔄 Hybrid Yaklaşım (İleri Seviye)

Eğer hem Python 2 hem Python 3 kullanmak istiyorsanız:

1. **Araç Tespiti**: Python 2 (Darknet) - `mobese-detection.py`
2. **Plaka Tespiti**: Python 3 (YOLOv8) - `mobese-lp-yolov8-detection.py`

Sistem zaten bunu destekliyor! `web_app.py` otomatik olarak:
- Python 3 ile YOLOv8'i dener
- Başarısız olursa Python 2 ile WPOD-NET kullanır

## ⚡ Hızlı Test

```bash
# Python 3 ortamında
conda activate base  # veya alpr_py3
python3 -c "from ultralytics import YOLO; model = YOLO('data/mobese-detector/mobese-lp-yolov8.pt'); print('Model yüklendi!')"
```

## 🐛 Sorun Giderme

### Hata: "No module named 'ultralytics'"
**Çözüm**: Python 3 ortamında `pip install ultralytics`

### Hata: "Python 3 bulunamadı"
**Çözüm**: Sistem otomatik olarak WPOD-NET kullanacak (sorun yok)

### Hata: "Model dosyası bulunamadı"
**Çözüm**: `data/mobese-detector/mobese-lp-yolov8.pt` dosyasının varlığını kontrol edin

## 📊 Performans Karşılaştırması

| Model | Python | Doğruluk | Hız | Durum |
|-------|--------|----------|-----|-------|
| YOLOv8 (best.pt) | Python 3 | %99.4 | ~3ms | ✅ Kuruldu |
| WPOD-NET | Python 2 | %75-85 | ~10ms | ✅ Mevcut |

## ✅ Özet

- **Python 2 ortamında**: WPOD-NET otomatik kullanılır (sorun yok)
- **Python 3 + Ultralytics**: `best.pt` kullanılır (en iyi performans)
- **Sistem her durumda çalışır!** 🎉

