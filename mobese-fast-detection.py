#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mobese için optimize edilmiş hızlı araç ve plaka tespiti
Daha düşük threshold ve optimize edilmiş işleme ile çok daha hızlı çalışır
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

		# Mobese için optimize edilmiş threshold (daha düşük = daha hızlı, daha fazla tespit)
		vehicle_threshold = .3  # Normal .5 yerine .3 (daha hızlı)

		vehicle_weights = 'data/vehicle-detector/yolo-voc.weights'
		vehicle_netcfg  = 'data/vehicle-detector/yolo-voc.cfg'
		vehicle_dataset = 'data/vehicle-detector/voc.data'

		vehicle_net  = dn.load_net(vehicle_netcfg, vehicle_weights, 0)
		vehicle_meta = dn.load_meta(vehicle_dataset)

		imgs_paths = image_files_from_folder(input_dir)
		imgs_paths.sort()

		if not isdir(output_dir):
			makedirs(output_dir)

		print('Mobese hızlı araç tespiti yapılıyor...')

		for i,img_path in enumerate(imgs_paths):

			bname = basename(splitext(img_path)[0])

			# Optimize edilmiş tespit - daha düşük threshold ile daha hızlı
			R,_ = detect(vehicle_net, vehicle_meta, img_path ,thresh=vehicle_threshold)

			# Sadece araçları filtrele
			R = [r for r in R if r[0] in ['car','bus']]

			if len(R):

				Iorig = cv2.imread(img_path)
				# Mobese için orijinal boyutta işle (daha doğru sonuç)
				# Sadece threshold düşürülerek hızlandırıldı
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

	except:
		traceback.print_exc()
		sys.exit(1)

	sys.exit(0)

