# Web Arayüzü - ALPR Sistemi

Python 2.7 ile uyumlu Flask tabanlı web arayüzü.

## Gereksinimler

- Python 2.7
- Flask (Python 2.7 uyumlu versiyon)
- Tüm proje bağımlılıkları (darknet, keras, tensorflow, opencv, numpy)

## Kurulum

1. Flask'ı yükleyin:
```bash
pip install flask
```

2. Darknet'in derlendiğinden emin olun:
```bash
cd darknet
make
cd ..
```

## Kullanım

### Web Arayüzünü Başlatma

```bash
bash run.sh -w
```

veya doğrudan:

```bash
python web_app.py
```

## Arayüz Özellikleri

- **Fotoğraf Yükleme**: 
  - Tıklayarak dosya seçebilirsiniz
  - Sürükle-bırak ile dosya yükleyebilirsiniz
- **Otomatik İşleme**: Yüklenen fotoğraf otomatik olarak işlenir
- **Görsel Sonuçlar**: 
  - Sarı kutular: Tespit edilen araçlar
  - Kırmızı çizgiler: Tespit edilen plakalar
  - Plaka numaraları görüntü üzerinde gösterilir
- **Metin Sonuçları**: Tespit edilen plaka numaraları metin olarak da gösterilir

## Tarayıcı Erişimi

Arayüz başlatıldıktan sonra:
- Yerel erişim: http://localhost:5000
- Ağ erişimi: http://0.0.0.0:5000 (diğer cihazlardan erişim için)

## Notlar

- İlk çalıştırmada modeller yükleneceği için biraz zaman alabilir
- Her görüntü işleme işlemi birkaç saniye sürebilir
- Birden fazla araç tespit edilirse, her biri için plaka okuma yapılır
- Maksimum dosya boyutu: 16MB

## Sorun Giderme

### "Flask bulunamadı" hatası
```bash
pip install flask
```

### "Darknet derlenmemiş" hatası
```bash
cd darknet
make
cd ..
```

### Model dosyaları bulunamıyor
`get-networks.sh` scriptini çalıştırarak model dosyalarını indirin:
```bash
bash get-networks.sh
```

### Port 5000 kullanımda
`web_app.py` dosyasındaki port numarasını değiştirebilirsiniz:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

