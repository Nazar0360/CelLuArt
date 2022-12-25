cheatsheet84 = {}
for i in range(0, 10): cheatsheet84[str(i)] = i
for i in range(0, 26): cheatsheet84[chr(ord('a') + i)] = i + 10
for i in range(0, 26): cheatsheet84[chr(ord('A') + i)] = i + 36
cheatsheet84 |= {
	"!": 62, "$": 63, "%": 64, "&": 65, "+": 66, "-": 67, ".": 68, "=": 69, "?": 70, "^": 71, "{": 72,
	"}": 73, "/": 74, "#": 75, "_": 76, "*": 77, "'": 78, ":": 79, ",": 80, "@": 81, "~": 82, "|": 83}

cheatsheet84 = {'to_base': {k: v for v, k in cheatsheet84.items()}, 'from_base': cheatsheet84}

def number_to_base(number: int, base: int, characters = None, negative_sign_symbol: str = '-') -> tuple[list[int], bool] | str:
	if characters is not None:
		assert base <= len(characters)
		if type(characters) is not dict:
			characters = {k: v for k, v in enumerate(characters)}
		if type(tuple(characters.keys())[0]) is str:
			characters = {k: v for v, k in characters.items()}
			
	base = abs(int(base))
	number = int(number)
	if number < 0:
		negative = True
		number = -number
	else:
		negative = False
	digits = []
	if number == 0:
		digits.append(0)
	while number:
		digits.append(int(number % base))
		number //= base
	digits = digits[::-1]
	if characters is None:
		return digits, negative
	else:
		return (negative_sign_symbol if negative else '') + ''.join(map(lambda n: characters[n], digits))

def number_from_base(number: str, base: int, characters = None, negative_sign_symbol:str = '-') -> int:
	if characters is not None:
		assert base <= len(characters)
		if type(characters) is not dict:
			characters = {k: v for k, v in enumerate(characters)}
		if type(tuple(characters.keys())[0]) is int:
			characters = {k: v for v, k in characters.items()}
	base = abs(int(base))
	number = str(number)
	if number[0] == negative_sign_symbol:
		negative = True
		number = number[1:]
	else:
		negative = False
	result = 0
	number = number[::-1]
	for index, digit in enumerate(number):
		result += characters[digit] * base ** index
	return result * (-1 if negative else 1)

base84 = lambda n: number_to_base(n, 84, cheatsheet84['to_base'], '>')
unbase84 = lambda n: number_from_base(n, 84, cheatsheet84['from_base'], '>')

if __name__ == '__main__':
	print(base84(1118481))
	print(unbase84('1/Hl'))
	print(cheatsheet84)
