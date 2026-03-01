#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mobese için YOLOv8 tabanlı araç tespiti
COCO dataset'inden car, bus, truck, motorcycle tespiti yapar
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
from os.path import splitext, basename
from src.label import Label, lwrite
from src.utils import crop_region, image_files_from_folder
from os import makedirs
from os.path import isdir


if __name__ == '__main__':

    try:
        
        input_dir  = sys.argv[1]
        output_dir = sys.argv[2]
        
        if not YOLOV8_AVAILABLE:
            print("YOLOv8 bulunamadi, normal mobese-detection.py kullanilmalı")
            print("Ultralytics yuklemek icin: pip install ultralytics")
            sys.exit(1)
        
        # YOLOv8 nano modeli kullan (çok hızlı ve hafif)
        # COCO dataset'i ile eğitilmiş, car, bus, truck, motorcycle içerir
        try:
            print('YOLOv8n modeli yukleniyor (ilk kullanimda otomatik indirilecek)...')
            model = YOLO('yolov8n.pt')  # Nano model - en hızlı
            print('Mobese YOLOv8 arac tespiti kullaniliyor (yolov8n.pt - COCO dataset)...')
        except Exception as e:
            print("YOLOv8 model yukleme hatasi: {}".format(str(e)))
            print("Model otomatik indirilecek, internet baglantisi gerekli")
            sys.exit(1)
        
        # Araç sınıfları (COCO dataset)
        vehicle_classes = [2, 3, 5, 7]  # car=2, motorcycle=3, bus=5, truck=7
        vehicle_names = ['car', 'motorcycle', 'bus', 'truck']
        
        if not isdir(output_dir):
            makedirs(output_dir)
        
        imgs_paths = image_files_from_folder(input_dir)
        imgs_paths.sort()
        
        for img_path in imgs_paths:
            bname = basename(splitext(img_path)[0])
            Iorig = cv2.imread(img_path)
            
            if Iorig is None:
                continue
            
            # YOLOv8 ile araç tespiti (düşük threshold - daha fazla tespit)
            results = model(Iorig, conf=0.15, classes=vehicle_classes, verbose=False)
            
            Lcars = []
            detected_vehicles = []
            
            for result in results:
                boxes = result.boxes
                if len(boxes) > 0:
                    for box in boxes:
                        # Bounding box koordinatları
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        
                        # Class name
                        class_name = model.names[cls]
                        
                        if class_name in vehicle_names:
                            detected_vehicles.append((class_name, conf))
                            
                            # Normalize koordinatlar (Label formatı için)
                            h, w = Iorig.shape[:2]
                            cx = (x1 + x2) / 2.0 / w
                            cy = (y1 + y2) / 2.0 / h
                            width = (x2 - x1) / w
                            height = (y2 - y1) / h
                            
                            tl = np.array([cx - width/2., cy - height/2.])
                            br = np.array([cx + width/2., cy + height/2.])
                            label = Label(0, tl, br)
                            
                            # Araç bölgesini kırp
                            Icar = crop_region(Iorig, label)
                            
                            Lcars.append(label)
                            
                            # Araç görüntüsünü kaydet
                            cv2.imwrite('%s/%s_%dcar.png' % (output_dir, bname, len(Lcars)-1), Icar)
            
            # Debug: Print detection results
            if len(detected_vehicles) > 0:
                vehicle_info = []
                for v in detected_vehicles[:5]:
                    try:
                        vehicle_info.append('{}({:.2f})'.format(v[0], v[1]))
                    except:
                        vehicle_info.append(str(v[0]))
                print('\t\t{} arac bulundu: {}'.format(len(detected_vehicles), vehicle_info))
            else:
                print('\t\tHic arac bulunamadi')
            
            # Araç koordinatlarını kaydet
            if len(Lcars) > 0:
                lwrite('%s/%s_cars.txt' % (output_dir, bname), Lcars)

    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)

