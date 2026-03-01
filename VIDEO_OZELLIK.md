# Video Üzerinden Plaka Tespiti Özelliği

## Eklenen Özellikler

### 1. Video Yükleme Desteği
- Web arayüzüne video dosyası yükleme özelliği eklendi
- Desteklenen formatlar: MP4, AVI, MOV, MKV, FLV, WMV
- Maksimum dosya boyutu: 100MB

### 2. Video İşleme
- Video frame'lerine ayrılıyor
- Her 5. frame'de plaka tespiti yapılıyor (performans için)
- Tespit edilen plakalar video üzerine çiziliyor
- İşlenmiş video oluşturuluyor

### 3. Sonuç Gösterimi
- İşlenmiş video tarayıcıda oynatılabiliyor
- Tespit edilen tüm plakalar listeleniyor
- İstatistikler gösteriliyor (araç sayısı, plaka sayısı, işlenen frame sayısı)

## Kullanım

### Web Arayüzü Üzerinden

1. Web arayüzünü başlatın:
   ```bash
   python web_app.py
   ```

2. Tarayıcıda http://localhost:5000 (veya gösterilen port) adresini açın

3. Video dosyasını yükleyin:
   - "Dosyayı sürükle veya tıkla" alanına video sürükleyin
   - Veya tıklayarak video dosyası seçin

4. "Videoyu İşle" butonuna tıklayın

5. İşlem tamamlanana kadar bekleyin (video boyutuna göre değişir)

6. Sonuçları görüntüleyin:
   - İşlenmiş video oynatılabilir
   - Tespit edilen plakalar listelenir
   - İstatistikler gösterilir

## Teknik Detaylar

### Video İşleme Parametreleri

- **frame_skip**: Her kaç frame'de bir işleme yapılacağı (varsayılan: 5)
  - Daha küçük değer = daha detaylı ama daha yavaş
  - Daha büyük değer = daha hızlı ama daha az detaylı

### Performans Notları

- Video işleme görüntü işlemeye göre çok daha uzun sürer
- Her frame için:
  1. Araç tespiti (YOLO)
  2. Plaka tespiti (WPOD-NET)
  3. OCR (Karakter tanıma)
  4. Sonuç çizimi
- 30 saniyelik bir video için yaklaşık 5-10 dakika sürebilir

### Sınırlamalar

- Maksimum video boyutu: 100MB
- İşlenmiş video 50MB'dan büyükse tarayıcıda gösterilemez (ancak işleme tamamlanır)
- Video codec desteği sistem bağımlıdır

## Sorun Giderme

### Video açılamıyor
- Video formatının desteklendiğinden emin olun
- Video codec'inin OpenCV tarafından desteklendiğinden emin olun

### Video işleme çok yavaş
- `frame_skip` parametresini artırın (web_app.py'de `process_video` fonksiyonunda)
- Daha kısa videolar deneyin
- Video çözünürlüğünü düşürün

### İşlenmiş video gösterilemiyor
- Video çok büyük olabilir (>50MB)
- Tarayıcı codec desteğini kontrol edin
- Video dosyasının oluşturulduğunu konsoldan kontrol edin

### Plaka tespit edilemiyor
- Video kalitesini kontrol edin
- Plakaların görünür olduğundan emin olun
- Daha fazla frame işlemek için `frame_skip` değerini düşürün

## Kod Yapısı

### Ana Fonksiyonlar

1. **process_video()**: Video işleme ana fonksiyonu
   - Video'yu açar
   - Frame'leri işler
   - Sonuçları birleştirir

2. **/upload endpoint**: Hem görüntü hem video için
   - Dosya tipini tespit eder
   - Uygun işleme fonksiyonunu çağırır

### Frontend Değişiklikleri

- Video önizleme desteği
- Video oynatıcı
- İşleme durumu göstergesi
- Frame sayısı istatistiği

## Gelecek İyileştirmeler

- [ ] İlerleme çubuğu (gerçek zamanlı)
- [ ] Video indirme özelliği
- [ ] Frame seçimi (hangi frame'lerin işleneceği)
- [ ] Çoklu video işleme
- [ ] Video kesme/kırpma özelliği
- [ ] Daha iyi hata yönetimi

