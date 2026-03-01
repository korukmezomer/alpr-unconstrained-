#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mobese için özel hızlı model kullanarak araç tespiti
Bu script mobese için ayrı, optimize edilmiş modeller kullanır
"""

import sys
import cv2
import numpy as np
import traceback

import darknet.python.darknet as dn

from src.label 				import Label, lwrite
from os.path 				import splitext, basename, isdir
from os 					import makedirs
from src.utils 				import crop_region, image_files_from_folder
from darknet.python.darknet import detect


if __name__ == '__main__':

	try:
	
		input_dir  = sys.argv[1]
		output_dir = sys.argv[2]

		# Mobese için özel model yolları
		# Öncelik sırası: YOLOv4-tiny > YOLOv3-tiny > Normal model
		mobese_vehicle_weights_yolov4 = 'data/mobese-detector/mobese-vehicle-yolov4-tiny.weights'
		mobese_vehicle_netcfg_yolov4  = 'data/mobese-detector/mobese-vehicle-yolov4-tiny.cfg'
		
		mobese_vehicle_weights = 'data/mobese-detector/mobese-vehicle.weights'
		mobese_vehicle_netcfg  = 'data/mobese-detector/mobese-vehicle.cfg'
		mobese_vehicle_dataset = 'data/mobese-detector/mobese-vehicle.data'
		
		# Fallback: Normal modeller
		normal_vehicle_weights = 'data/vehicle-detector/yolo-voc.weights'
		normal_vehicle_netcfg  = 'data/vehicle-detector/yolo-voc.cfg'
		normal_vehicle_dataset = 'data/vehicle-detector/voc.data'
		
		# Mobese modellerini kontrol et (öncelik: YOLOv4-tiny > YOLOv3-tiny)
		import os
		use_yolov4 = os.path.exists(mobese_vehicle_weights_yolov4) and os.path.exists(mobese_vehicle_netcfg_yolov4)
		use_yolov3 = os.path.exists(mobese_vehicle_weights) and os.path.exists(mobese_vehicle_netcfg)
		use_mobese_model = use_yolov4 or use_yolov3
		
		if use_mobese_model:
			if use_yolov4:
				# YOLOv4-tiny kullan (daha iyi doğruluk)
				vehicle_weights = mobese_vehicle_weights_yolov4
				vehicle_netcfg  = mobese_vehicle_netcfg_yolov4
				vehicle_dataset = mobese_vehicle_dataset
				vehicle_threshold = .01  # ÇOK DÜŞÜK threshold - maksimum tespit için
				print('Mobese özel modeli kullanılıyor (YOLOv4-tiny - threshold=0.01 - MAKSIMUM TESPIT)...')
			else:
				# YOLOv3-tiny kullan (fallback)
				vehicle_weights = mobese_vehicle_weights
				vehicle_netcfg  = mobese_vehicle_netcfg
				vehicle_dataset = mobese_vehicle_dataset
				vehicle_threshold = .01  # ÇOK DÜŞÜK threshold - maksimum tespit için
				print('Mobese özel modeli kullanılıyor (YOLOv3-tiny - threshold=0.01 - MAKSIMUM TESPIT)...')
		else:
			vehicle_weights = normal_vehicle_weights
			vehicle_netcfg  = normal_vehicle_netcfg
			vehicle_dataset = normal_vehicle_dataset
			vehicle_threshold = .01  # ÇOK DÜŞÜK threshold - maksimum tespit için
			print('Mobese modeli bulunamadı, normal model kullanılıyor (threshold=0.01 - MAKSIMUM TESPIT)...')

		print('   Model yolu: {}'.format(vehicle_weights))
		print('   Config yolu: {}'.format(vehicle_netcfg))
		print('   Dataset yolu: {}'.format(vehicle_dataset))
		print('   Threshold: {}'.format(vehicle_threshold))
		
		vehicle_net  = dn.load_net(vehicle_netcfg, vehicle_weights, 0)
		vehicle_meta = dn.load_meta(vehicle_dataset)
		print('   ✅ Model yüklendi!')

		imgs_paths = image_files_from_folder(input_dir)
		imgs_paths.sort()

		if not isdir(output_dir):
			makedirs(output_dir)

		for i,img_path in enumerate(imgs_paths):

			bname = basename(splitext(img_path)[0])

			R,_ = detect(vehicle_net, vehicle_meta, img_path ,thresh=vehicle_threshold)

		# COCO dataset classes: car=2, bus=5 (0-indexed: car=2, bus=5)
		# But YOLO returns class names, so check for 'car' and 'bus'
		# Tüm araç tiplerini dahil et
		vehicle_classes = ['car', 'bus', 'truck', 'motorcycle', 'van', 'suv', 'pickup']
		R_filtered = [r for r in R if r[0].lower() in [v.lower() for v in vehicle_classes]]
		
		# Debug: Print all detections before filtering
		if len(R) > 0:
			print('\t\tToplam {} tespit, {} araç tipi: {}'.format(len(R), len(R_filtered), [r[0] for r in R[:5]]))
		else:
			print('\t\t⚠️ Darknet hiç tespit yapamadı (threshold={})'.format(vehicle_threshold))
		
		R = R_filtered
		
		# Debug: Print detection results
		if len(R) > 0:
			print('\t\t✅ {} araç bulundu: {}'.format(len(R), [r[0] for r in R]))
			
			Iorig = cv2.imread(img_path)
			WH = np.array(Iorig.shape[1::-1],dtype=float)
			Lcars = []

			for i,r in enumerate(R):

				cx,cy,w,h = (np.array(r[2])/np.concatenate( (WH,WH) )).tolist()
				tl = np.array([cx - w/2., cy - h/2.])
				br = np.array([cx + w/2., cy + h/2.])
				label = Label(0,tl,br)
				Icar = crop_region(Iorig,label)

				Lcars.append(label)

				cv2.imwrite('%s/%s_%dcar.png' % (output_dir,bname,i),Icar)

			lwrite('%s/%s_cars.txt' % (output_dir,bname),Lcars)
		else:
			# Hiç tespit yok - tüm tespitleri göster
			if len(R) == 0:
				print('\t\t⚠️ Hiç tespit yok - threshold={} çok yüksek olabilir veya görüntüde araç yok'.format(vehicle_threshold))
				print('\t\t   Görüntü boyutu kontrol ediliyor...')
				Iorig = cv2.imread(img_path)
				if Iorig is not None:
					h, w = Iorig.shape[:2]
					print('\t\t   Görüntü boyutu: {}x{}'.format(w, h))

	except:
		traceback.print_exc()
		sys.exit(1)

	sys.exit(0)

