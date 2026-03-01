ALPR Sistemi – Türkiye’ye Özel Geliştirilmiş Hibrit Plaka Tanıma Platformu
👨‍💻 Geliştirici

Ömer Körükmez

🎯 Proje Hakkında

Bu proje, canlı MOBESE kamera akışları ve statik görüntüler üzerinden gerçek zamanlı plaka tespiti ve plaka okuma yapabilen hibrit bir ALPR (Automatic License Plate Recognition) sistemidir.

Sistem, temel olarak ECCV 2018 çalışması olan
License Plate Detection and Recognition in Unconstrained Scenarios mimarisini temel almakta olup, Türkiye şartlarına ve MOBESE altyapısına uygun şekilde genişletilmiş ve modernleştirilmiştir.

Projede klasik WPOD-NET yaklaşımı korunmuş, buna ek olarak Türkiye plakalarına özel eğitilmiş YOLOv8 tabanlı modern bir plaka tespit modeli entegre edilmiştir.

🧠 Sistem Mimarisi
🔹 1️⃣ Klasik ALPR Pipeline (Python 2 – Orijinal Mimari)
4

Bu yapı aşağıdaki adımlardan oluşur:

Araç Tespiti (YOLO / Darknet)

Plaka Bölgesi Tespiti (WPOD-NET)

Karakter Segmentasyonu

OCR ile Plaka Okuma

CSV çıktısı üretimi

Bu pipeline Python 2.7 + Keras 2.2.4 + TensorFlow 1.x ortamında çalışmaktadır.

🔹 2️⃣ Türkiye’ye Özel Geliştirilmiş YOLOv8 Entegrasyonu (Python 3)
4

Bu projede ek olarak:

🇹🇷 Türkiye plaka formatına özel eğitilmiş YOLOv8 best.pt modeli

Python 3 + Ultralytics altyapısı

Canlı MOBESE kamera akışı desteği

Otomatik fallback mekanizması

Çalışma Mantığı
1️⃣ Önce: YOLOv8 best.pt (Python 3)
2️⃣ Başarısız olursa: WPOD-NET (Python 2)

Bu hibrit yapı sayesinde:

Daha yüksek doğruluk

Gerçek zamanlı performans

Esnek mimari

Eski sistemlerle uyumluluk

sağlanmıştır.

🔥 Özellikler

✅ Canlı MOBESE Kamera Desteği
✅ Türkiye Plakalarına Özel Eğitimli Model
✅ YOLOv8 Entegrasyonu
✅ Otomatik Python 2/3 Hibrit Çalışma
✅ Darknet CPU/GPU Desteği
✅ Web Arayüzü (Flask)
✅ Toplu Görüntü İşleme
✅ CSV Raporlama
✅ Otomatik Model Fallback

⚙️ Kurulum Talimatları
1️⃣ Ortamı Aktifleştirin
conda activate alpr_py2
2️⃣ Darknet Derleme (İlk Kurulum)
cd darknet
make
cd ..
3️⃣ Model Dosyalarını İndirin
bash get-networks.sh
4️⃣ YOLOv8 Kurulumu (Türkiye Modeli İçin)
python3 -m pip install ultralytics

Model yolu:

data/mobese-detector/mobese-lp-yolov8.pt
🌐 Web Arayüzü Başlatma
python web_app.py

Tarayıcıdan açın:

http://localhost:5000
📦 Toplu İşleme
bash run.sh -i samples/test -o /tmp/output -c /tmp/output/results.csv
📊 Log Kontrolü
YOLOv8 Kullanıldığında:
✅ Mobese YOLOv8 plaka tespiti modeli kullanılıyor...
Frame X - ✅ best.pt kullanıldı!
Fallback Durumunda:
⚠️ YOLOv8 başarısız, WPOD-NET kullanılıyor...
🧩 Hibrit Python Mimarisi
İşlem	Python	Model
Araç Tespiti	Python 2	YOLO
Plaka Tespiti	Python 3	YOLOv8 (best.pt)
Fallback	Python 2	WPOD-NET
OCR	Python 2	Darknet OCR
🚦 Performans

YOLOv8 Nano yapı → Gerçek zamanlı tespit

YOLOv3-tiny → Hızlı araç algılama

Optimize edilmiş threshold değerleri

Frame skipping desteği

🎓 Akademik Referans

Bu sistem aşağıdaki çalışmayı temel alarak genişletilmiştir:

License Plate Detection and Recognition in Unconstrained Scenarios
ECCV 2018

Ancak proje, Türkiye MOBESE altyapısı ve modern YOLOv8 mimarisi ile yeniden tasarlanmış ve geliştirilmiştir.

🛡️ Not

Bu sistem:

Trafik analizi

Akıllı şehir sistemleri

Otopark otomasyonu

Güvenlik uygulamaları

için kullanılabilir.

👑 Sonuç

Bu proje klasik ALPR mimarisi ile modern YOLOv8 yaklaşımını birleştirerek:

🇹🇷 Türkiye’ye özel, gerçek zamanlı, hibrit ve yüksek doğruluklu bir plaka tanıma sistemi sunmaktadır.