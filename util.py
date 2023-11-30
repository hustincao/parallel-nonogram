folder = 'created-tests'
file = '20x20'

solution_file = open(f'{folder}/{file}/solution', 'r')
lines = solution_file.readlines()

board = []
for index, line in enumerate(lines):
    l = []
    for i in line.strip():
        l.append(int(i))
    board.append(l)
# print(board)
print(len(board), len(board[0]))


# for col in board:
#     num_ones = 0
#     for col in row:
#         if col == 0 and num_ones > 0:
#             print(num_ones, end=" ")
#             num_ones = 0
#         elif col == 1:
#             num_ones+=1
#     if row[len(row) - 1] == 1:
#             print(num_ones, end=" ")
#     print()

for row in board:
    num_ones = 0
    for col in row:
        if col == 0 and num_ones > 0:
            print(num_ones, end=" ")
            num_ones = 0
        elif col == 1:
            num_ones+=1
    if row[len(row) - 1] == 1:
            print(num_ones, end=" ")
    print()


