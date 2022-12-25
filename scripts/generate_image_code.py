import level_code as level_code
from from_lua import *
import pathlib as pl
import numpy as np
import cv2

class ImgCode(level_code.LevelCode):
	def __init__(self, k3code: str):
		super().__init__(k3code)
	
	@staticmethod
	def from_image(img: np.ndarray, title = '', subtitle = '', border_type = 1):
		if img is None: 
			return

		cells = ''
		width = img.shape[1]
		height = img.shape[0]
		for y in range(0, height):
			for x in range(0, width):
				r, g, b = img[y, x]
				dec_color = (r << 16) + (g << 8) + b
				dec_color = dec_color if dec_color > 0 else 1
				paint_color = base84(int(dec_color))
				cells += f'(5I[<paint<){len(paint_color)}{paint_color}'
		return ImgCode.from_data('K3', title, subtitle, width, height, border_type, cells)

# print(ImgCode.from_image(cv2.imread(str((pl.Path(__file__).parents[1] / 'media' / 'Sans_undertale.jpg').absolute()))) is None)
print(ImgCode.from_image(cv2.imread("E:\\Users\\Hlop-1\\Downloads\\CelLua_Machine_v2.-1.6tb3\\media_to_level_code\\media\\Sans_undertale.jpg")) is None)
print('done')
