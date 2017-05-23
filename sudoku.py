import copy
import random

def getCellIndex(width, coords): # 'coords' is a dict of axis:value for each dimension
	return sum(map(lambda dim: coords[dim] * int(pow(width,dim)), coords))

class Cell:
	#possibilities = [] # list of sybols that this cell could be
	def __init__(self, size):
		self.possibilities = []
		self.cellsToCompareTo = []

class Row:
	
	def __init__(self, width, axis, coords):
		self.cellIndicies = []
		self.axis = axis
		for i in range(width):
			coords[axis] = i
			self.cellIndicies.append(getCellIndex(width, coords))

class Box:
	
	def __init__(self, numcells, axis1, axis1coord, axis2, axis2coord, coords):
		self.coords = {} # coordinates of the plane that the box is in
		self.cellIndicies = []
		self.width = int(pow(numcells,0.5))
		for x in range(axis1coord, axis1coord+self.width):
			coords[axis1] = x
			for y in range(axis2coord, axis2coord+self.width):
				coords[axis2] = y
				self.cellIndicies.append(getCellIndex(numcells,coords))

class Sheet:
	def __init__(self, width, axis1, axis2, coords):
		self.width = width
		self.axis1 = axis1
		self.axis2 = axis2
		self.coords = coords # a dict (length dims-2) of coordinates (axis:value), locating this plane on the remaining axes
		self.rows = []
		self.boxes = []
		self.coords = coords
		# create all of the rows
		for i in range(width):
			row1coords = copy.deepcopy(coords)
			row1coords[axis2] = i
			self.rows.append(Row(width, axis1, row1coords))
			row2coords = copy.deepcopy(coords)
			row2coords[axis1] = i
			self.rows.append(Row(width, axis2, row2coords))
		# create the boxes
		boxwidth = int(pow(width,0.5))
		for x in range(0, width, boxwidth):
			for y in range(0, width, boxwidth):
				self.boxes.append(Box(width, axis1, x, axis2, y, coords))
		return
	
	def getCellIndex(self, col, row):
		return self.rows[row].cellIndicies[col]

class Game:
	width = 0
	dims = 0
	cells = []
	planes = [] # a list of tuples of 2 axis
	sheets = []
	def __init__(self, dims, width):
		self.width = width
		self.dims = dims
		print('Creating ' + str(pow(width, dims)) + ' cells....')
		for i in range(pow(width, dims)):
			self.cells.append(Cell(width))
		# Create the Sheets
		if dims == 2:
			print('Creating 1 sheet.')
			self.sheets.append(Sheet(width,0,1,{})) # a 2-D sudoku has one plane that covers dimensions #0 and #1, and needs no location
		else:
			# create all possible combinations of axes and coordinate values
			print('Creating axis combinations...')
			combos = []
			for axis in range(dims):
				newcombos = []
				# for (almost) every existing axis combination, there is that same combination along with the current axis
				for combo in combos:
					if len(combo) < dims - 2: # no point in creating axis combos that will be thrown out...
						for i in range(width):
							newcombo = copy.deepcopy(combo) # deepcopy is very necessary!
							newcombo[axis] = i
							newcombos.append(newcombo)
				# there are also (probably) axis combinations that don't have any of the previous axes but do have this one
				for i in range(width):
					newcombos.append({axis:i})
				combos += newcombos
			
			# remove duplicate and too-short axis combinations
			coords = []
			for combo in combos:
				if len(combo) == dims-2 and combo not in coords:
					coords.append(combo)
			print('Creating ' + str(len(coords)) + ' sheets...', flush=True)
			for coord in coords:
				axes = []
				# The two axes that don't locate the sheet are the axes that the sheet lies in. Find them.
				# There should hopefully always be two.
				for axis in range(dims):
					if axis not in coord:
						axes.append(axis)
				self.sheets.append(Sheet(width,axes[0],axes[1],coord))

	
def printSheet(sheet, game):
	print('↑' + str(sheet.axis1) + ' →' + str(sheet.axis2) + '    ' + str(sheet.coords))
	maxposlen = 1 + len(str(sheet.width)) # number of characters for each possibility
	boxwidth = int(pow(sheet.width,0.5))
	coords = sheet.coords
	for y in range(sheet.width):
		coords[sheet.axis2] = y
		for x in range(sheet.width):
			coords[sheet.axis1] = x
			val = str(game.cells[getCellIndex(sheet.width, coords)].possibilities[0])
			pad = ' ' * (maxposlen - len(val))
			print(pad,val,end=' ')
			if ((x+1) % boxwidth) == 0 and (x+1) < sheet.width:
				print(' |', end='')
		print('')
		if ((y+1) % boxwidth) == 0 and (y+1) < sheet.width:
			for x in range(sheet.width):
				print(('-'*maxposlen)+'--',end='')
				if ((x+1) % boxwidth) == 0 and (x+1) < sheet.width:
					print('-+', end='')
			print('')
	
def solveCell(cellIndex, size, game, restOfCells):
	print('.',end='',flush=True)
	# if a cell hasn't been processed before, give it a list of all cells it should be compared to
	if game.cells[cellIndex].cellsToCompareTo == []:
		rowsAndBoxes = []
		for sheet in sudoku.sheets:
			for row in sheet.rows:
				if cellIndex in row.cellIndicies:
					rowsAndBoxes.append(row)
			for box in sheet.boxes:
				if cellIndex in box.cellIndicies:
					rowsAndBoxes.append(box)
		otherCellIndicies = []
		for rORb in rowsAndBoxes:
			for otherCellIndex in rORb.cellIndicies:
				if otherCellIndex != cellIndex:
					if not (otherCellIndex in otherCellIndicies):
						otherCellIndicies.append(otherCellIndex)
		game.cells[cellIndex].cellsToCompareTo = otherCellIndicies
	# find out what values this cell can't be
	otherCellValues = {}
	for otherCellIndex in game.cells[cellIndex].cellsToCompareTo:
		if game.cells[otherCellIndex].possibilities != []:
			otherCellValues[game.cells[otherCellIndex].possibilities[0]] = 1
	possibilities = []
	for possibility in range(size):
		if possibility not in otherCellValues:
			possibilities.append(possibility)
	# try each thing that this cell can be
	for possibility in possibilities:
		game.cells[cellIndex].possibilities = [possibility]
		if len(restOfCells) == 0:
			return [possibility]
		nextCell = restOfCells.pop()
		solution = solveCell(nextCell, size, game, restOfCells)
		if solution != None:
			return [possibility] + solution
		restOfCells.append(nextCell)
	# if execution got here, then there were no possibilities that resulted in solutions
	print('\b \b',end='',flush=True)
	game.cells[cellIndex].possibilities = []
	return None

# Begin game execution!
print("Welcom to m^2 sudoku in n dimensions!")
dims = -1
while dims < 2:
	dims = input("How many dimensions? (minimum 2, typically 2): ")
	if dims == '':
		dims = 2
	try:
		dims = int(dims)
	except:
		print('"' + dims + '" is not an integer >= 2')
		dims = -1
print("Sudoku in " + str(dims) + " dimensions.")
size = -1
while size < 1:
	size = input("Square root of the width of the board? (minimum 1, typically 3): ")
	if size == '':
		size = 3
	try:
		size = int(size)
	except:
		print('"' + size + '" is not an integer >= 1')
		size = -1
size = pow(size,2)
print("A " + ((str(size)+'x')*dims)[:-1] + ' sudoku game.')

sudoku = Game(dims, size)

mayberandom = input("Solve in random order? [y/N]: ")
if len(mayberandom) >  0 and (mayberandom[0]=='y' or mayberandom[0]=='Y'):
	solveOrder = list(range(len(sudoku.cells)))
	random.shuffle(solveOrder)
else:
	# Produce a list of cells, sorted by distance from the 0 corner.
	# Deterministic but reasonably fast.
	print("Ordering cells...",flush=True)
	solveOrder = []
	for distanceFromCorner in range(0, 1+(dims*(size-1))):
		# generate every dims-length list of positive integers that adds to distanceFromCorner
		sumLists = [[]]
		for dim in range(dims):
			newLists = []
			for dist in range(0,size):
				for sumList in sumLists:
					if sum(sumList) + dist <= distanceFromCorner:
						newList = copy.deepcopy(sumList)
						newList.append(dist)
						newLists.append(newList)
			sumLists += newLists
		properSumLists = []
		for sumList in sumLists:
			if len(sumList) == dims:
				if sum(sumList) == distanceFromCorner:
					properSumLists.append(sumList)
		# turn those lists into coordinates
		coords = []
		for sumList in properSumLists:
			coord = {}
			for dim in range(len(sumList)):
				coord[dim] = sumList[dim]
			coords.append(coord)
		# get the cells corresponding to those coordinates and add them to the list
		for coord in coords:
			solveOrder.append(getCellIndex(size,coord))
	# do a sanity check
	for i in range(len(sudoku.cells)):
		if not (i in solveOrder):
			print('CELL ' + str(i) + ' NOT IN SOLVE ORDER! BIG WHOOPSIES!')
			solveOrder.append(i)
print('Solving cells...',flush=True)
firstCellIndex = solveOrder.pop()
solution = solveCell(firstCellIndex, size, sudoku, solveOrder)
print('\n')
if solution:
	for sheet in sudoku.sheets:
		printSheet(sheet, sudoku)
		print()
		print()
else:
	print('No solution found.')