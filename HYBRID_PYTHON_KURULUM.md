# Hybrid Python 2/3 Kurulum Kılavuzu

## ✅ Mükemmel Haber!

`alpr_py2` ortamınızda **hem Python 2 hem Python 3 mevcut!**

```
python  → Python 2.7.18 (Anaconda)
python3 → Python 3.14.0 (Homebrew)
```

## 🎯 Sistem Yapılandırması

### Normal İşlemler (Python 2)
- ✅ `vehicle-detection.py` → `python` (Python 2)
- ✅ `license-plate-detection.py` → `python` (Python 2)
- ✅ `license-plate-ocr.py` → `python` (Python 2)
- ✅ `gen-outputs.py` → `python` (Python 2)
- ✅ `mobese-detection.py` → `python` (Python 2, Darknet)

### Mobese İşlemleri (Python 3)
- ✅ `mobese-lp-yolov8-detection.py` → `python3` (Python 3, YOLOv8 best.pt)
- ✅ Fallback: `mobese-lp-detection.py` → `python` (Python 2, WPOD-NET)

## 📦 Ultralytics Kurulumu

### Adım 1: Ultralytics'i Python 3'e Kur

```bash
conda activate alpr_py2
python3 -m pip install --user ultralytics
```

### Adım 2: Kontrol Et

```bash
python3 -c "from ultralytics import YOLO; print('✅ Kuruldu!')"
```

### Adım 3: Model Testi

```bash
python3 -c "from ultralytics import YOLO; import os; model_path = 'data/mobese-detector/mobese-lp-yolov8.pt'; print('Model:', '✅ Var' if os.path.exists(model_path) else '❌ Yok'); model = YOLO(model_path) if os.path.exists(model_path) else None; print('Model yüklendi!' if model else 'Model yüklenemedi')"
```

## 🚀 Sistem Nasıl Çalışıyor?

### Normal Video/Resim İşleme
```python
# Python 2 ile çalışır
vehicle_cmd = ['python', 'vehicle-detection.py', ...]
lp_cmd = ['python', 'license-plate-detection.py', ...]
```

### Mobese Canlı Akış
```python
# Araç tespiti: Python 2
vehicle_cmd = ['python', 'mobese-detection.py', ...]

# Plaka tespiti: Python 3 (YOLOv8) veya Python 2 (WPOD-NET)
if python3_available:
    lp_cmd = ['python3', 'mobese-lp-yolov8-detection.py', ...]
else:
    lp_cmd = ['python', 'mobese-lp-detection.py', ...]
```

## 📊 Script - Python Eşleştirmesi

| Script | Python Sürümü | Model | Ortam |
|--------|---------------|-------|-------|
| `vehicle-detection.py` | Python 2 | YOLO-voc | `alpr_py2` |
| `license-plate-detection.py` | Python 2 | WPOD-NET | `alpr_py2` |
| `license-plate-ocr.py` | Python 2 | Darknet OCR | `alpr_py2` |
| `gen-outputs.py` | Python 2 | - | `alpr_py2` |
| `mobese-detection.py` | Python 2 | YOLOv4-tiny | `alpr_py2` |
| `mobese-lp-yolov8-detection.py` | **Python 3** | **best.pt (YOLOv8)** | `alpr_py2` (python3) |
| `mobese-lp-detection.py` | Python 2 | WPOD-NET | `alpr_py2` |

## ✅ Avantajlar

1. **Tek Ortam**: Her şey `alpr_py2` ortamında
2. **Otomatik Seçim**: Sistem doğru Python sürümünü kullanır
3. **Fallback**: Python 3 yoksa Python 2 kullanılır
4. **En İyi Performans**: 
   - Normal işlemler: Python 2 (mevcut modeller)
   - Mobese: Python 3 (best.pt - %99.4 doğruluk)

## 🔧 Sorun Giderme

### Hata: "No module named 'ultralytics'"
```bash
python3 -m pip install --user ultralytics
```

### Hata: "python3 bulunamadı"
- Sistem otomatik olarak Python 2 ile WPOD-NET kullanacak
- Sorun yok, sistem çalışmaya devam eder

### Hata: "Model dosyası bulunamadı"
```bash
ls -lh data/mobese-detector/mobese-lp-yolov8.pt
# 6.0 MB olmalı
```

## 🎉 Özet

**Durum**: ✅ Hazır!

- ✅ `alpr_py2` ortamında hem Python 2 hem Python 3 var
- ✅ Normal işlemler Python 2 ile çalışıyor
- ✅ Mobese işlemleri Python 3 ile çalışacak (ultralytics kurulduktan sonra)
- ✅ Sistem otomatik fallback yapıyor

**Sadece yapmanız gereken**:
```bash
conda activate alpr_py2
python3 -m pip install --user ultralytics
python web_app.py
```

**Sistem otomatik olarak**:
- Normal işlemler için Python 2 kullanır
- Mobese için Python 3 kullanır (varsa)
- Python 3 yoksa Python 2'ye fallback yapar

Her şey hazır! 🚀

