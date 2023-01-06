from functions import *
import pyperclip
import attr
import copy
	
class Level:
	class Cells(np.ndarray):
		def __new__(cls, level_width: int, level_height: int, depth: int):
			level_width, level_height, depth = int(level_width), int(level_height), int(depth)
			assert level_width > 0 and level_height > 0 and depth > 0
			return super().__new__(cls, shape=(depth, level_height, level_width), dtype=object)
		def __init__(self, level_width: int, level_height: int, depth: int):
			for index in np.ndindex(self.shape):
				z, y, x = index 
				self[z, y, x] = Level.Cells.Cell()
		def apply_function(self, func):
			for index, cell in np.ndenumerate(self):
				z, y, x = index
				self[z, y, x] = copy.deepcopy(func(x=x, y=y, z=z, id=cell.id, rot=cell.rot, vars=cell.vars, placeable=cell.placeable))
		@attr.s()
		class Cell:
			id: str | int = attr.ib(default=0)
			rot: int = attr.ib(default=0)
			vars: dict = attr.ib(factory=dict)

			def copy(self):
				return Level.Cells.Cell(self.id, self.rot, self.vars.copy())

			@property
			def encoded(self):
				if type(self.id) is int:
					code = encode_value(base84(self.id*4+self.rot), int)
				else: code = encode_value(self.id) + str(self.rot)

				if self.vars:
					for key, value in self.vars.items():
						code += f'[{encode_value(key)}{encode_value(value)}'
				return code
			
			@staticmethod
			def decode_cell(code: str) -> tuple[object, int, str]:
				# *note: this function decodes only a first cell and returns the rest of a code
				if not code: return Level.Cells.Cell(), 0, code
				z = 0
				if code[0] == '\\': z, code = decode_value(code[1:])
				value, code = decode_value(code)
				if type(value) is str: id, rot, code = value, *decode_value(code)
				else: id, rot = value // 4, value % 4
				vars = {}
				if code and code[0] == '[':
					while code[0] == '[':
						key, code = decode_value(code[1:])
						value, code = decode_value(code)
						vars |= {key: value}
				return Level.Cells.Cell(id, rot, vars), z, code
	
	class Placeables(np.ndarray):
		@attr.s()
		class Placeable:
			id:  str | int | None = attr.ib(default=None)

			def copy(self):
				return Level.Placeables.Placeable(self.id)

			@property
			def encoded(self):
				if not self.id:
					return ''
				return f']{encode_value(self.id)}'
			
			@staticmethod
			def decode_placeable(code: str) -> tuple[object, str]:
				# *note: this function decodes only a first placeable and returns the rest of a code
				if code[0] == ']': 
					id, code = decode_value(code[1:])
					return Level.Placeables.Placeable(id), code
				return Level.Placeables.Placeable(), code

		def __new__(cls, level_width: int, level_height: int):
			level_width, level_height = int(level_width), int(level_height)
			assert level_width > 0 and level_height > 0
			return super().__new__(cls, shape=(level_height, level_width), dtype=object)

		def __init__(self, level_width: int, level_height: int):
			for index in np.ndindex(self.shape):
				y, x = index 
				self[y, x] = Level.Placeables.Placeable()
	
	def __repr__(self):
		return f'LevelCode({self.__dict__})'
	
	def encoded_cells(self):
		encoded_cells = ''
		for y in range(self.height):
			for x in range(self.width):
				encoded_cells += self.placeables[y, x].encoded
				for z in range(self.depth):
					cell = self.cells[z, y, x]
					if (cell.id != 0) or (z == 0):
						back_slash = '\\'
						encoded_cells += f'{(back_slash + base84characters[z]) if (z != 0) else ""}{cell.encoded}'
		return to_zlib_base64(encoded_cells)
	
	@staticmethod
	def loadK3(k3code: str):
		if (code_type := type(k3code)) != str:
			raise TypeError(f'Code should be a string, not {code_type}')
		if k3code[-1] == ';':
			k3code = k3code[:-1]
		code_parts = k3code.replace(':', ';').split(sep=';')
		assert code_parts[0] == 'K3', f'Only K3 codes are supported ({code_parts[0]} ones does not)'
		match len(code_parts):
			case 7:
				level = Level(unbase84(code_parts[3]), unbase84(code_parts[4]), unbase84(code_parts[5]), title=code_parts[1], subtitle=code_parts[2])
				str_cells = from_zlib_base64(code_parts[6])
			case 6:
				level = Level(unbase84(code_parts[2]), unbase84(code_parts[3]), unbase84(code_parts[4]), title=code_parts[1])
				str_cells = from_zlib_base64(code_parts[5])
			case 5:
				level = Level(unbase84(code_parts[1]), unbase84(code_parts[2]), unbase84(code_parts[3]))
				str_cells = from_zlib_base64(code_parts[4])
			case _:
				raise ValueError(f'{k3code} isn\'t a valid code')
		assert str_cells, f'{k3code} isn\'t a valid code'
		for y in range(level.height):
			for x in range(level.width):
				placeable, str_cells = Level.Placeables.Placeable.decode_placeable(str_cells)
				level.set_placeable(x, y, placeable)
				cell, z, str_cells = Level.Cells.Cell.decode_cell(str_cells)
				level.place_cell(x, y, cell, z=z)
				if str_cells and str_cells[0] == '\\':
					cell, z, str_cells = Level.Cells.Cell.decode_cell(str_cells)
					level.place_cell(x, y, cell, z=z)
		return level
	
	def __init__(self, width: int = 100, height: int = 100, border_type: int = 1, *, title='', subtitle='', depth: int = 2):
		self._border_type = int(border_type) % 12
		self._title = str(title)
		self._subtitle = str(subtitle)
		self._cells = Level.Cells(width, height, depth)
		self._placeables = Level.Placeables(width, height)
	
	def get_cell(self, x: int, y: int, z: int) -> object:
		return self.cells[z, y, x]

	def place_cell(self, x: int, y: int, cell: object, *, z: int = 0):
		self.cells[z, y, x] = cell.copy()
	
	def get_placeable(self, x: int, y: int) -> object:
		return self.placeables[y, x]
	
	def set_placeable(self, x: int, y: int, placeable: object):
		self.placeables[y, x] = placeable.copy()

	def fill(self, cell: Cells.Cell = Cells.Cell(), placeable: Placeables.Placeable = Placeables.Placeable(), *, start_pos: tuple[int, int] = None, end_pos: tuple[int, int] = None, layers: tuple[int, ...] = (0,)):
		if not (start_pos or end_pos):
			for index, _cell, _placeable in self:
				if index[0] not in layers: continue
				_cell.id, _cell.rot, _cell.vars = cell.id, cell.rot, cell.vars.copy()
				_placeable.id = placeable.id
		else:
			if not (start_pos and end_pos): start_pos, end_pos = [min(start_pos[i], end_pos[i]) for i in range(2)], [max(start_pos[i], end_pos[i]) for i in range(2)]
			if start_pos is None: start_pos = (0, 0)
			if end_pos is None: end_pos = (self.height - 1, self.width - 1)
			for index, _cell, _placeable in self:
				if index[0] not in layers: continue
				if (end_pos[0] >= index[1] >= start_pos[0]) and (end_pos[1] >= index[2] >= start_pos[1]):
					_cell.id, _cell.rot, _cell.vars = cell.id, cell.rot, cell.vars.copy()
					_placeable.id = placeable.id
	
	def paint_from_image(self, img: np.ndarray, *, start_pos: tuple[int, int] = None, end_pos: tuple[int, int] = None, layers: tuple[int, ...] = (0, )):
		if not (start_pos or end_pos):
			img = cv2.resize(img, self.placeables.shape)
			for index, _cell, _ in self:
				if index[0] not in layers: continue
				_cell.vars |= {'paint': decimal_color_from_rgb(img[index[1], index[2]][::-1])}
		else:
			if not (start_pos and end_pos): start_pos, end_pos = [min(start_pos[i], end_pos[i]) for i in range(2)], [max(start_pos[i], end_pos[i]) for i in range(2)]
			if start_pos is None: start_pos = (0, 0)
			if end_pos is None: end_pos = (self.height - 1, self.width - 1)
			start_pos, end_pos = np.array(start_pos), np.array(end_pos)
			img = cv2.resize(img, (end_pos - start_pos + 1)[::-1], interpolation=cv2.INTER_NEAREST)
			for index, _cell, _ in self:
				if index[0] not in layers: continue
				if (end_pos[0] >= index[1] >= start_pos[0]) and (end_pos[1] >= index[2] >= start_pos[1]):
					_cell.vars |= {'paint': decimal_color_from_rgb(img[index[1]-start_pos[0], index[2]-start_pos[1]][::-1])}
	
	def mark_coordinates_with_coins(self, *, layers = (0,)):
		for index, _cell, _ in self:
			if index[0] not in layers: continue
			length = max(len(str(v)) for v in self.cells.shape)
			_cell.vars |= {'coins': index[2] * 10 ** length + index[1]}
	
	def copy_level_code(self):
		pyperclip.copy(self.code)
	
	def __iter__(self):
		for index, cell in np.ndenumerate(self.cells):
			z, y, x = index
			placeable = self.placeables[y, x]
			yield index, cell, placeable

	@property
	def code(self):
		return f'K3{f":{self.title}" if self.title else ""}{(":" if not self.title else "") + (f":{self.subtitle}" if self.subtitle else "")};'\
				f'{base84(self.width)};{base84(self.height)};{base84(self.border_type)};{self.encoded_cells()};'
	@property
	def width(self):
		return self._cells.shape[2]
	@property
	def height(self):
		return self._cells.shape[1]
	@property
	def depth(self):
		return self._cells.shape[0]
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
	@property
	def placeables(self):
		return self._placeables


if __name__ == '__main__':
	Cell = Level.Cells.Cell
	Placeable = Level.Placeables.Placeable
	
	level = Level()
	level.fill(Cell(4))
	level.paint_from_image(cv2.imread(relative_path2absolute('../images/sans_head.jpg')), start_pos=(4, 16), end_pos=(35, 47))
	level.copy_level_code()
