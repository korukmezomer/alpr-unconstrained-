#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mobese için özel hızlı model kullanarak plaka tespiti
Bu script mobese için ayrı, optimize edilmiş modeller kullanır
"""

import sys, os
import keras
import cv2
import traceback

from src.keras_utils 			import load_model
from glob 						import glob
from os.path 					import splitext, basename
from src.utils 					import im2single
from src.keras_utils 			import load_model, detect_lp
from src.label 					import Shape, writeShapes


if __name__ == '__main__':

	try:
		
		input_dir  = sys.argv[1]
		output_dir = input_dir
		
		# 2. parametre opsiyonel (geriye uyumluluk için)
		# Model yolu script içinde belirleniyor

		# Mobese için özel model yolu
		mobese_lp_model_path = 'data/mobese-detector/mobese-lp-detector.h5'
		
		# Fallback: Normal model
		normal_lp_model_path = 'data/lp-detector/wpod-net_update1.h5'
		
		# Mobese modelini kontrol et
		use_mobese_model = os.path.exists(mobese_lp_model_path)
		
		if use_mobese_model:
			wpod_net_path = mobese_lp_model_path
			lp_threshold = .3  # Mobese için optimize edilmiş threshold (daha hızlı)
			print('Mobese özel plaka modeli kullanılıyor...')
		else:
			wpod_net_path = normal_lp_model_path
			lp_threshold = .3  # Fallback için düşük threshold
			print('Mobese plaka modeli bulunamadı, normal model kullanılıyor (optimize edilmiş)...')
		
		wpod_net = load_model(wpod_net_path)

		imgs_paths = glob('%s/*car.png' % input_dir)

		for i,img_path in enumerate(imgs_paths):

			bname = splitext(basename(img_path))[0]
			Ivehicle = cv2.imread(img_path)

			# Mobese için optimize edilmiş boyutlandırma (çok daha hızlı)
			if use_mobese_model:
				# Mobese modeli için çok daha küçük input (maksimum hız)
				ratio = float(max(Ivehicle.shape[:2]))/min(Ivehicle.shape[:2])
				side  = int(ratio*160.)  # Çok daha küçük (288 -> 160)
				bound_dim = min(side + (side%(2**4)), 400)  # Çok daha küçük (608 -> 400)
			else:
				# Normal model için standart boyut
				ratio = float(max(Ivehicle.shape[:2]))/min(Ivehicle.shape[:2])
				side  = int(ratio*288.)
				bound_dim = min(side + (side%(2**4)),608)

			Llp,LlpImgs,_ = detect_lp(wpod_net,im2single(Ivehicle),bound_dim,2**4,(240,80),lp_threshold)

			if len(LlpImgs):
				Ilp = LlpImgs[0]
				Ilp = cv2.cvtColor(Ilp, cv2.COLOR_BGR2GRAY)
				Ilp = cv2.cvtColor(Ilp, cv2.COLOR_GRAY2BGR)

				s = Shape(Llp[0].pts)

				cv2.imwrite('%s/%s_lp.png' % (output_dir,bname),Ilp*255.)
				writeShapes('%s/%s_lp.txt' % (output_dir,bname),[s])

	except:
		traceback.print_exc()
		sys.exit(1)

	sys.exit(0)

