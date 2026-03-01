#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mobese için YOLOv8 tabanlı plaka tespiti
best.pt modelini kullanarak Türk plakalarını tespit eder
"""

import sys
import cv2
import numpy as np
import traceback
import os

try:
    from ultralytics import YOLO
    YOLOV8_AVAILABLE = True
except ImportError:
    YOLOV8_AVAILABLE = False
    print("Ultralytics YOLOv8 bulunamadı. Yüklemek için: pip install ultralytics")

from glob import glob
from os.path import splitext, basename, dirname, abspath


if __name__ == '__main__':

    try:
        
        input_dir  = sys.argv[1]
        output_dir = input_dir
        
        # Mobese için YOLOv8 plaka tespiti modeli
        mobese_lp_yolov8_path = 'data/mobese-detector/mobese-lp-yolov8.pt'
        
        # Fallback: Normal WPOD-NET modeli
        normal_lp_model_path = 'data/lp-detector/wpod-net_update1.h5'
        
        # YOLOv8 modelini kontrol et
        use_yolov8 = YOLOV8_AVAILABLE and os.path.exists(mobese_lp_yolov8_path)
        
        if use_yolov8:
            print('✅ Mobese YOLOv8 plaka tespiti modeli kullanılıyor (best.pt - Türk plakaları için özel eğitilmiş - %99.4 doğruluk)...')
            print('   📁 Model yolu: {}'.format(os.path.abspath(mobese_lp_yolov8_path)))
            print('   📊 Model boyutu: {:.1f} MB'.format(os.path.getsize(mobese_lp_yolov8_path) / (1024*1024)))
            
            # YOLOv8 modelini yükle (best.pt)
            print('   🔄 best.pt modeli yükleniyor...')
            model = YOLO(mobese_lp_yolov8_path)
            print('   ✅ best.pt modeli başarıyla yüklendi!')
            
            # Araç görüntülerini bul
            imgs_paths = glob('%s/*car.png' % input_dir)
            
            for img_path in imgs_paths:
                bname = splitext(basename(img_path))[0]
                Ivehicle = cv2.imread(img_path)
                
                if Ivehicle is None:
                    continue
                
                # YOLOv8 ile plaka tespiti (düşük threshold - daha fazla tespit)
                results = model(Ivehicle, conf=0.2, verbose=False)  # Düşük threshold
                
                # Sonuçları işle
                for result in results:
                    boxes = result.boxes
                    if len(boxes) > 0:
                        # En yüksek confidence'lı plakayı al
                        best_box = boxes[0]
                        x1, y1, x2, y2 = best_box.xyxy[0].cpu().numpy()
                        conf = best_box.conf[0].cpu().numpy()
                        
                        # Plaka bölgesini kırp
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        Ilp = Ivehicle[y1:y2, x1:x2]
                        
                        if Ilp.size > 0:
                            # Plaka görüntüsünü kaydet
                            cv2.imwrite('%s/%s_lp.png' % (output_dir, bname), Ilp)
                            
                            # Plaka koordinatlarını kaydet (WPOD-NET formatına uygun)
                            try:
                                from src.label import Shape, writeShapes
                                
                                # Normalize koordinatlar
                                h, w = Ivehicle.shape[:2]
                                pts = np.array([
                                    [float(x1)/w, float(y1)/h],
                                    [float(x2)/w, float(y1)/h],
                                    [float(x2)/w, float(y2)/h],
                                    [float(x1)/w, float(y2)/h]
                                ])
                                
                                s = Shape(pts)
                                writeShapes('%s/%s_lp.txt' % (output_dir, bname), [s])
                            except ImportError:
                                # Eğer src.label yoksa, sadece görüntüyü kaydet
                                pass
                            
                            print('\t\tPlaka tespit edildi (conf: {:.2f})'.format(conf))
        else:
            # Fallback: Normal WPOD-NET kullan
            print('YOLOv8 modeli bulunamadı veya ultralytics yüklü değil, WPOD-NET kullanılıyor...')
            
            # Fallback: Normal WPOD-NET kullan
            try:
                from src.keras_utils import load_model, detect_lp
                from src.utils import im2single
                from src.label import Shape, writeShapes
                
                wpod_net = load_model(normal_lp_model_path)
                imgs_paths = glob('%s/*car.png' % input_dir)
                
                for img_path in imgs_paths:
                    bname = splitext(basename(img_path))[0]
                    Ivehicle = cv2.imread(img_path)
                    
                    if Ivehicle is None:
                        continue
                    
                    # WPOD-NET ile plaka tespiti
                    ratio = float(max(Ivehicle.shape[:2]))/min(Ivehicle.shape[:2])
                    side  = int(ratio*200.)  # Küçük input
                    bound_dim = min(side + (side%(2**4)), 512)
                    
                    Llp, LlpImgs, _ = detect_lp(wpod_net, im2single(Ivehicle), bound_dim, 2**4, (240,80), 0.3)
                    
                    if len(LlpImgs):
                        Ilp = LlpImgs[0]
                        Ilp = cv2.cvtColor(Ilp, cv2.COLOR_BGR2GRAY)
                        Ilp = cv2.cvtColor(Ilp, cv2.COLOR_GRAY2BGR)
                        
                        s = Shape(Llp[0].pts)
                        cv2.imwrite('%s/%s_lp.png' % (output_dir, bname), Ilp*255.)
                        writeShapes('%s/%s_lp.txt' % (output_dir, bname), [s])
            except Exception as e:
                print("WPOD-NET fallback hatası: {}".format(str(e)))
                traceback.print_exc()

    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)

