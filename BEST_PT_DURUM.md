# best.pt Kullanım Durumu

## ✅ Sistem Yapılandırması

### Mobese Plaka Tespiti Akışı

1. **İlk Deneme**: best.pt (YOLOv8) - Python 3 + Ultralytics
2. **Fallback**: WPOD-NET - Python 2 (eğer best.pt başarısız olursa)

## 🔍 Kontrol Noktaları

### 1. Model Dosyası
```bash
ls -lh data/mobese-detector/mobese-lp-yolov8.pt
# ✅ 6.0 MB olmalı
```

### 2. Python 3
```bash
conda activate alpr_py2
python3 --version
# ✅ Python 3.8.12 olmalı (conda)
```

### 3. Ultralytics
```bash
conda activate alpr_py2
/opt/miniconda3/envs/alpr_py2/bin/python3 -c "from ultralytics import YOLO; print('✅ Kurulu')"
```

### 4. best.pt Test
```bash
conda activate alpr_py2
/opt/miniconda3/envs/alpr_py2/bin/python3 -c "from ultralytics import YOLO; model = YOLO('data/mobese-detector/mobese-lp-yolov8.pt'); print('✅ Model yüklendi!')"
```

## 📊 Log Mesajları

### best.pt Kullanıldığında:
```
✅ Mobese YOLOv8 plaka tespiti modeli kullanılıyor (best.pt - Türk plakaları için özel eğitilmiş - %99.4 doğruluk)...
   Model yolu: data/mobese-detector/mobese-lp-yolov8.pt
Frame X - ✅ best.pt kullanıldı!
```

### WPOD-NET Kullanıldığında:
```
⚠️ YOLOv8 plaka tespiti başarısız (ultralytics yüklü değil olabilir), WPOD-NET kullanılıyor...
```

## 🎯 Durum Kontrolü

Sistem çalışırken logları kontrol edin:

1. **best.pt kullanılıyor mu?**
   - Log'da "✅ best.pt kullanıldı!" mesajını arayın
   - Log'da "Mobese YOLOv8 plaka tespiti modeli kullanılıyor" mesajını arayın

2. **WPOD-NET kullanılıyor mu?**
   - Log'da "WPOD-NET kullanılıyor" mesajını arayın
   - Bu durumda best.pt kullanılmıyor demektir

## 🔧 Sorun Giderme

### best.pt Kullanılmıyorsa:

1. **Ultralytics kurulu değil:**
   ```bash
   conda activate alpr_py2
   /opt/miniconda3/envs/alpr_py2/bin/python3 -m pip install ultralytics
   ```

2. **Python 3 bulunamıyor:**
   ```bash
   conda activate alpr_py2
   conda install -c conda-forge python=3.8 -y
   ```

3. **Model dosyası yok:**
   ```bash
   ls -lh data/mobese-detector/mobese-lp-yolov8.pt
   # Eğer yoksa, best.pt dosyasını kopyalayın
   ```

## ✅ Özet

**best.pt kullanımı için gereksinimler:**
- ✅ Model dosyası: `data/mobese-detector/mobese-lp-yolov8.pt` (6.0 MB)
- ✅ Python 3.8+ (conda ortamında)
- ✅ Ultralytics kütüphanesi

**Sistem otomatik olarak:**
1. Önce best.pt'yi dener (Python 3 + Ultralytics)
2. Başarısız olursa WPOD-NET'e fallback yapar (Python 2)

**Log mesajları ile kontrol edebilirsiniz!**

