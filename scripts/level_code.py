import zlib, base64
from from_lua import *

class LevelCode:
	def __repr__(self):
		return f'LevelCode({self.__dict__})'
	
	@staticmethod
	def data_to_code(code_format, title, subtitle, width, height, border_type, cells):
		return ';'.join(
			(
				code_format, base84(width), base84(height), base84(border_type),
				f'{(":"+title) if len(title) > 0 else ""}{(":"+subtitle) if len(subtitle) > 0 else ""}',
				base64.b64encode(zlib.compress(bytes(cells, 'utf-8'))).decode("utf-8"), ''
			)).replace(';;', ';')
	
	def from_data(code_format, title, subtitle, width, height, border_type, cells):
		self = LevelCode.__new__(LevelCode)
		self._code_format = code_format
		self._title = title
		self._subtitle = subtitle
		self._width = width
		self._height = height
		self._border_type = border_type
		self._cells = cells
		return self

	def __init__(self, k3code: str):
		"""
		It takes a string, checks if it's a valid K3 code, and if it is, it sets the object's properties to
		the values in the code
		
		:param k3code: The code to be parsed
		:type k3code: str
		"""
		if (code_type := type(k3code)) != str:
			raise TypeError(f'Code should be a string, not {code_type}')
		
		if k3code[-1] == ';':
			k3code = k3code[:-1]
		code_parts = k3code.replace(':', ';').split(sep=';')
		self._code_format = code_parts[0]
		self._width = unbase84(code_parts[1])
		self._height = unbase84(code_parts[2])
		self._border_type = unbase84(code_parts[3])
		match len(code_parts):
			case 7:
				self._title = code_parts[4]
				self._subtitle = code_parts[5]
				self._cells = zlib.decompress(base64.b64decode(code_parts[6]))
			case 6:
				self._title = code_parts[4]
				self._subtitle = ''
				self._cells = zlib.decompress(base64.b64decode(code_parts[5]))
			case 5:
				self._title = ''
				self._subtitle = ''
				self._cells = zlib.decompress(base64.b64decode(code_parts[4]))
			case _:
				raise ValueError(f'Code {k3code} isn\'t valid')

	@property
	def code(self):
		return LevelCode.data_to_code(self._code_format, self.title, self.subtitle, self.width, self.height, self.border_type, self.cells)

	@property
	def code_format(self):
		return self._code_format
	@property
	def width(self):
		return self._width
	@property
	def height(self):
		return self._height
	@property
	def border_type(self):
		return self._border_type
	@property
	def title(self):
		return self._title
	@property
	def subtitle(self):
		return self._subtitle
	@property
	def cells(self):
		return self._cells

if __name__ == '__main__':
	c = LevelCode('K3;a;a;1;eNrTMPWMtilIzMwrsdE0tTPU98jRMPXEhYhXOVwR2WEFALpuU1U=;')
	print(c.cells, c.code, sep='\n')
