import pathlib as pl
import zlib, base64
import numpy as np
import cv2

base84characters = ''
for i in range(0, 10): base84characters += str(i)
for i in range(0, 26): base84characters += chr(ord('a') + i)
for i in range(0, 26): base84characters += chr(ord('A') + i)
base84characters += "!$%&+-.=?^{}/#_*':,@~|"

def number_to_base(number: int, base: int, *, characters: str = '0123456789ABCDEF', negative_sign_symbol: str = '-') -> str:
	number, base, characters, negative_sign_symbol = int(number), abs(int(base)), str(characters), str(negative_sign_symbol)
	assert len(characters) >= base
	assert negative_sign_symbol not in characters
	if number < 0:
		negative = True
		number = -number
	else:
		negative = False
	digits = []
	if number == 0:
		return characters[0]
	while number:
		digits.append(int(number % base))
		number //= base
	digits = digits[::-1]
	return (negative_sign_symbol if negative else '') + ''.join(map(lambda n: characters[n], digits))

def number_from_base(number: str, base: int, *, characters: str = '0123456789ABCDEF', negative_sign_symbol: str = '-') -> int:
	number, base, characters, negative_sign_symbol = str(number), abs(int(base)), str(characters), str(negative_sign_symbol)
	assert len(characters) >= base
	assert negative_sign_symbol not in characters
	if number[0] == negative_sign_symbol:
		negative = True
		number = number[1:]
	else:
		negative = False
	result = 0
	number = number[::-1]
	for index, digit in enumerate(number):
		n = characters.find(digit)
		assert n != -1
		result += n * base ** index
	return result * (-1 if negative else 1)

base84 =	lambda n: number_to_base	(n, 84, characters=base84characters, negative_sign_symbol='>')
unbase84 =	lambda n: number_from_base	(n, 84, characters=base84characters, negative_sign_symbol='>')

def to_zlib_base64(s: str) -> str:
	return base64.b64encode(zlib.compress(bytes(s, 'utf-8'))).decode('utf-8')

def from_zlib_base64(s: str) -> str:
	return zlib.decompress(base64.b64decode(s)).decode('utf-8')

def decimal_color_from_rgb(rgb):
	r, g, b = rgb
	return int((r << 16) + (g << 8) + b)

def relative_path2absolute(path: str):
	path = path.replace('/', '\\')
	path = path.replace('..\\', f'{str(pl.Path(__file__).parents[1])}\\')
	path = path.replace('.\\', f'{str(pl.Path(__file__).parent)}\\')
	return path

def encode_value(value: int | str | bool, _type: type = None) -> str:
	"""
	It encodes a value into a string
	
	:param value: The value to encode
	:type value: int | str | bool
	:param _type: The type that the value will be interpreted as
	:type _type: type
	:return: A string.
	"""
	if _type is None: _type = type(value)
	if _type is int:
		if type(value) is int: value = base84(value)
		if len(value) == 1: return value
		elif len(value) == 2: return f'({value}'
		else: return f'){len(value)}{value}'
	elif _type is str:
		return f'<{value}<'
	elif _type is bool:
		if value: return '1'
		else: return ''
	else: raise TypeError(f'Unsupported type: {_type}')

def decode_value(code: str) -> tuple[int | str, str]:
	# *note: this function decodes only a first value in a code and returns rest
	if code[0] == '<':
		return code[1:code.find('<', 1)], code[code.find('<', 1)+1:]
	elif code[0] == ')':
		return unbase84(code[2:int(code[1]) + 2]), code[int(code[1])+2:]
	elif code[0] == '(':
		return unbase84(code[1:3]), code[3:]
	else: return unbase84(code[0]), code[1:]
	

if __name__ == '__main__':
	img = cv2.imread('D:\\Ded\\Documents\\Nazar\\CelLuArt\\images\\rgb_wheel.png')
	img = cv2.resize(img, (10, 10))
	cv2.imshow('1', img)
	cv2.waitKeys(0)
