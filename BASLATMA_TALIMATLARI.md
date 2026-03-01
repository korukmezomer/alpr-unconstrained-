# ALPR Sistemi - Başlatma Talimatları

## Hızlı Başlangıç (Web Arayüzü)

### 1. Python 2 Ortamını Aktifleştirin
```bash
conda activate alpr_py2
```

### 2. Proje Dizinine Gidin
```bash
cd "/Users/omerkorukmez/Desktop/yazılım mühendisliğinde gelişmeler 3/alpr-unconstrained"
```

### 3. Darknet'i Derleyin (İlk Kurulum)
```bash
cd darknet
make
cd ..
```

### 4. Model Dosyalarını İndirin (İlk Kurulum)
```bash
bash get-networks.sh
```

### 5. Web Arayüzünü Başlatın

**Seçenek 1: run.sh script'i ile**
```bash
bash run.sh -w
```

**Seçenek 2: Doğrudan Python ile**
```bash
python web_app.py
```

### 6. Tarayıcıda Açın
Web sunucusu başladıktan sonra tarayıcınızda şu adresi açın:
- **http://localhost:5000** (veya gösterilen port numarası)

---

## Toplu İşleme (Batch Processing)

Birden fazla görüntüyü toplu olarak işlemek için:

```bash
bash run.sh -i samples/test -o /tmp/output -c /tmp/output/results.csv
```

Parametreler:
- `-i`: Görüntülerin bulunduğu klasör
- `-o`: Çıktı klasörü
- `-c`: Sonuçların kaydedileceği CSV dosyası

---

## Gereksinimler Kontrolü

### Flask Kurulumu
```bash
pip install flask
```

### Model Dosyaları Kontrolü
Aşağıdaki dosyaların mevcut olduğundan emin olun:
- `data/lp-detector/wpod-net_update1.h5`
- `data/ocr/ocr-net.weights`
- `data/vehicle-detector/yolo-voc.weights`

### Darknet Kontrolü
```bash
ls darknet/libdarknet.so
```
Bu dosya varsa Darknet derlenmiş demektir.

---

## Sorun Giderme

### Port 5000 Kullanımda
Sistem otomatik olarak 5001, 5002 gibi portları deneyecektir. Konsolda gösterilen port numarasını kullanın.

### "Araç bulunamadı" Hatası
- Görüntüde araç olup olmadığını kontrol edin
- Konsolda hata mesajlarını kontrol edin
- Model dosyalarının doğru yüklendiğinden emin olun

### Import Hataları
```bash
# Gerekli paketleri kontrol edin
python -c "import cv2, numpy, keras, darknet"
```

---

## Örnek Kullanım

1. Web arayüzünü başlatın: `python web_app.py`
2. Tarayıcıda http://localhost:5000 adresini açın
3. "Dosya Seç" butonuna tıklayın veya görüntüyü sürükle-bırak yapın
4. Sistem otomatik olarak:
   - Araçları tespit eder
   - Plakaları bulur
   - Plaka numaralarını okur
5. Sonuçlar ekranda görüntülenir

---

## Notlar

- İlk çalıştırmada modeller yükleneceği için biraz zaman alabilir
- Her görüntü işleme işlemi birkaç saniye sürebilir
- Maksimum dosya boyutu: 16MB
- Desteklenen formatlar: JPG, PNG

