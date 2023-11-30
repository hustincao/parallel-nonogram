import numpy
import os
from PIL import Image

filename = '68092'
num_cols = 34
num_rows = 28


im = Image.open(f"img/medium/{filename}.png")
folder = f'tests/medium/{filename}'
if not os.path.isdir(folder):
    os.mkdir(folder)



width, height = im.size
cell_width = width/num_cols
cell_height = height/num_rows

board = numpy.full((num_rows, num_cols), 0)

rgb_im = im.convert('1')


# Read in board
for i in range(num_rows):
    for j in range(num_cols):

        (x, y) = (cell_height * j + cell_height/2, cell_width * i + cell_width/2)
        board[i][j] = 1 if rgb_im.getpixel((x, y)) == 0 else 0

# Write constraints
with open(f'{folder}/constraints', "x") as f:
    constraint_text = ''
    constraint_text += f'{num_cols} {num_rows}\n'
    
    for x in range(num_cols):
        num_ones = 0
        for y in range(num_rows):
            cell = board[y][x]
            if cell == 0 and num_ones > 0:
                constraint_text += f'{num_ones} '
                num_ones = 0
            elif cell == 1:
                num_ones += 1
        if board[num_rows-1][x] == 1:
            constraint_text += f'{num_ones} '
        constraint_text = constraint_text.rstrip()
        constraint_text += '\n'
    
    

    for y in range(num_rows):
        num_ones = 0
        for x in range(num_cols):
            cell = board[y][x]

            if cell == 0 and num_ones > 0:
                constraint_text += f'{num_ones} '
                num_ones = 0
            elif cell == 1:
                num_ones += 1
        if board[y][num_cols-1] == 1:
            constraint_text += f'{num_ones} '
        constraint_text = constraint_text.rstrip()
        constraint_text += '\n'
    constraint_text = constraint_text.rstrip()
    f.write(constraint_text)

# Write solution
with open(f'{folder}/solution', 'x') as f2:
    board_text = ''
    for y in range(num_rows):
        for x in range(num_cols):
            board_text += f'{board[y][x]}'
        board_text += "\n"
    board_text = board_text.rstrip()
    f2.write(board_text)
# print(board)
