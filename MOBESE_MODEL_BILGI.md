# Mobese Modelleri - Kurulum Bilgileri

## İndirilen Modeller

### ✅ Araç Tespiti Modeli - YOLOv3-tiny
- **Model**: YOLOv3-tiny (çok hızlı, hafif)
- **Boyut**: 34 MB
- **Kaynak**: https://pjreddie.com/darknet/yolo/
- **Özellikler**:
  - Normal YOLO'dan 3-5x daha hızlı
  - Çok daha küçük model boyutu
  - COCO dataset üzerinde eğitilmiş (car ve bus sınıfları içerir)
  - Real-time işleme için optimize edilmiş

**Dosyalar**:
- `mobese-vehicle.weights` ✅ (34 MB - İndirildi)
- `mobese-vehicle.cfg` ✅ (İndirildi)
- `mobese-vehicle.data` ✅ (Oluşturuldu)
- `mobese-vehicle.names` ✅ (Oluşturuldu)

### ✅ Plaka Tespiti Modeli
- **Model**: WPOD-NET (mevcut modelin kopyası)
- **Boyut**: 6.5 MB
- **Not**: Şu anda mevcut model kullanılıyor. Daha hafif bir alternatif bulunursa değiştirilebilir.

**Dosyalar**:
- `mobese-lp-detector.h5` ✅ (6.5 MB - Kopyalandı)

## Performans Karşılaştırması

### YOLOv3-tiny vs Normal YOLO
- **Hız**: ~3-5x daha hızlı
- **Boyut**: ~10x daha küçük (34MB vs 250MB+)
- **Doğruluk**: Biraz daha düşük ama yeterli
- **Kullanım**: Real-time uygulamalar için ideal

### Mobese Optimizasyonları
- Threshold: 0.3 (daha hızlı tespit)
- Input size: 160 (normal 288'den çok daha küçük)
- Bound dim: 400 (normal 608'den çok daha küçük)
- Frame skip: 5 (normal 10'dan daha sık)

## Kullanım

Modeller otomatik olarak kullanılır. Mobese Seyret butonuna tıkladığınızda:
1. Sistem önce mobese modellerini kontrol eder
2. Varsa mobese modellerini kullanır (YOLOv3-tiny)
3. Yoksa normal modelleri optimize edilmiş şekilde kullanır

## Test

Modelleri test etmek için:

```bash
# Test görüntüsü ile
python mobese-detection.py test_input/ test_output/
python mobese-lp-detection.py test_output/
```

## Notlar

- YOLOv3-tiny COCO dataset üzerinde eğitilmiş, car ve bus sınıflarını içerir
- Mobese modelleri mevcut modellerden tamamen bağımsızdır
- Sistem otomatik olarak en hızlı modelleri kullanır
- Daha hızlı plaka modeli bulunursa `mobese-lp-detector.h5` değiştirilebilir

