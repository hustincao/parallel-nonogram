import sys
from numba import cuda
import numpy as np
from itertools import combinations

UNFILLED = 0 # White
FILLED = 1 # Black
UNKNOWN = 6

def generate_row_possibilities(HEIGHT, WIDTH, ROW_CONSTRAINTS, row_answers):
    # Generate all possible row answers
    for r in range(HEIGHT):
        n_groups = len(ROW_CONSTRAINTS[r])
        n_empty = WIDTH - sum(ROW_CONSTRAINTS[r]) - n_groups + 1
        possible_row_answers = np.ndarray(shape=(0, WIDTH), dtype=np.int32)
        for p in combinations(range(n_groups + n_empty), n_groups):
            possible_answer = np.ones(shape=(WIDTH), dtype=np.int32)
            for i in range(len(p)):
                start_index = p[i]
                length = ROW_CONSTRAINTS[r][i]
                for index in range(length):
                    possible_answer[start_index + index + i] = 2
            possible_row_answers = np.vstack(
                (possible_row_answers, possible_answer))
        row_answers[r] = possible_row_answers


def generate_col_possibilities(HEIGHT, WIDTH, COL_CONSTRAINTS, col_answers):
    for c in range(WIDTH):
        n_groups = len(COL_CONSTRAINTS[c])
        n_empty = HEIGHT - sum(COL_CONSTRAINTS[c]) - n_groups + 1
        possible_col_answers = np.ndarray(shape=(0, HEIGHT), dtype=np.int32)
        for p in combinations(range(n_groups + n_empty), n_groups):
            possible_answer = np.ones(shape=(HEIGHT), dtype=np.int32)
            for i in range(len(p)):
                start_index = p[i]
                length = COL_CONSTRAINTS[c][i]
                for index in range(length):
                    possible_answer[start_index + index + i] = 2
            possible_col_answers = np.vstack(
                (possible_col_answers, possible_answer))
        col_answers[c] = possible_col_answers


def intersect_row_possibilities(HEIGHT, WIDTH, row_answers, board):
    for r in range(HEIGHT):
        line = np.zeros(shape=(WIDTH), dtype=np.int32)

        for i in range(WIDTH):
            line[i] = row_answers[r][0][i]
        for j in range(1, len(row_answers[r])):
            for i in range(WIDTH):
                if line[i] != row_answers[r][j][i]:
                    line[i] = 0

        for i in range(WIDTH):
            if board[r][i] == 0:
                board[r][i] = line[i]
            elif line[i] != 0 and board[r][i] != line[i]:
                print("ERROR: Illegal constraints")


def intersect_col_possibilities(HEIGHT, WIDTH, col_answers, board):
    for c in range(WIDTH):
        line = np.zeros(shape=(HEIGHT), dtype=np.int32)
        for i in range(HEIGHT):
            line[i] = col_answers[c][0][i]
        for j in range(1, len(col_answers[c])):
            for i in range(HEIGHT):
                if line[i] != col_answers[c][j][i]:
                    line[i] = 0

        for i in range(WIDTH):
            if board[i][c] == 0:
                board[i][c] = line[i]
            elif line[i] != 0 and board[i][c] != line[i]:
                print("ERROR: Illegal constraints")


def remove_row_possibilities(HEIGHT, WIDTH, row_answers, board):
    # With new board, delete impossible answers
    for r in range(HEIGHT):
        for row in reversed(range(len(row_answers[r]))):
            # print(row)
            answer = row_answers[r][row]
            # print(answer)
            for i in range(WIDTH):
                if board[r][i] != 0 and board[r][i] != answer[i]:
                    # print(f"delete answer {row} in row {r}")
                    row_answers[r] = np.delete(row_answers[r], row, 0)
                    break
            # print(row)


def remove_col_possibilities(HEIGHT, WIDTH, col_answers, board):
    for c in range(WIDTH):
        for col in reversed(range(len(col_answers[c]))):
            answer = col_answers[c][col]
            for i in range(HEIGHT):
                if board[i][c] != 0 and board[i][c] != answer[i]:
                    # print(f"delete answer {col} in col {c}")
                    col_answers[c] = np.delete(col_answers[c], col, 0)
                    break


def is_completed(HEIGHT, WIDTH, board):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if board[i][j] == 0:
                return False
    return True


def is_correct(HEIGHT, WIDTH, board, solution):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if board[i][j] != solution[i][j]:
                return False
    return True


def main():
    file1 = open('tests/0/constraints', 'r')
    lines = file1.readlines()
    HEIGHT, WIDTH = [int(s) for s in lines[0].strip().split()]
    print(HEIGHT, WIDTH)
    ROW_CONSTRAINTS = []
    COL_CONSTRAINTS = []

    for index, line in enumerate(lines[1:]):
        if index < HEIGHT:
            COL_CONSTRAINTS.append([int(s) for s in line.strip().split( )])
        else:
            ROW_CONSTRAINTS.append([int(s) for s in line.strip().split( )])
    # print(ROW_CONSTRAINTS)
    # print(COL_CONSTRAINTS)
    # sys.exit()
    # ROW_CONSTRAINTS = [[2], [1, 2], [3], [2], [1, 1, 1]]
    # COL_CONSTRAINTS = [[1, 1], [2], [1, 1], [3], [4]]
    # solution = np.array([[2, 2, 1, 1, 1], 
    #                      [1, 2, 1, 2, 2], 
    #                      [1, 1, 2, 2, 2], 
    #                      [1, 1, 1, 2, 2], 
    #                      [2, 1, 2, 1, 2]])

    # WIDTH = len(COL_CONSTRAINTS)
    # HEIGHT = len(ROW_CONSTRAINTS)

    board = np.zeros(shape=(HEIGHT, WIDTH), dtype=np.int32)
    # print(board)
    # row_answers = np.ndarray(shape=(5), dtype=np.dtype(object))

    row_answers = np.full(shape=(HEIGHT), fill_value=[0 for _ in range(HEIGHT)], dtype=np.dtype(object))
    col_answers = np.full(shape=(WIDTH), fill_value=[
                          0 for _ in range(WIDTH)], dtype=np.dtype(object))

    generate_row_possibilities(HEIGHT, WIDTH, ROW_CONSTRAINTS, row_answers)
    generate_col_possibilities(HEIGHT, WIDTH, COL_CONSTRAINTS, col_answers)

    counter = 0
    while True:

        intersect_row_possibilities(HEIGHT, WIDTH, row_answers, board)
        intersect_col_possibilities(HEIGHT, WIDTH, col_answers, board)

        remove_row_possibilities(HEIGHT, WIDTH, row_answers, board)
        remove_col_possibilities(HEIGHT, WIDTH, col_answers, board)
        counter += 1
        if is_completed(HEIGHT, WIDTH, board) or counter > 10:
            break

    print(board)

    # Generate all possible row answers
    # for r in range(HEIGHT):
    #     n_groups = len(ROW_CONSTRAINTS[r])
    #     n_empty = WIDTH - sum(ROW_CONSTRAINTS[r]) - n_groups + 1
    #     possible_row_answers = np.ndarray(shape=(0, WIDTH), dtype=np.int32)
    #     for p in combinations(range(n_groups + n_empty), n_groups):
    #         possible_answer = np.ones(shape=(WIDTH), dtype=np.int32)
    #         for i in range(len(p)):
    #             start_index = p[i]
    #             length = ROW_CONSTRAINTS[r][i]
    #             for index in range(length):
    #                 possible_answer[start_index + index + i] = 2
    #         possible_row_answers = np.vstack((possible_row_answers, possible_answer))
    #     row_answers[r] = possible_row_answers

    # # Generate all possible col answers
    # for c in range(WIDTH):
    #     n_groups = len(COL_CONSTRAINTS[c])
    #     n_empty = HEIGHT - sum(COL_CONSTRAINTS[c]) - n_groups + 1
    #     possible_col_answers = np.ndarray(shape=(0, HEIGHT), dtype=np.int32)
    #     for p in combinations(range(n_groups + n_empty), n_groups):
    #         possible_answer = np.ones(shape=(HEIGHT), dtype=np.int32)
    #         for i in range(len(p)):
    #             start_index = p[i]
    #             length = COL_CONSTRAINTS[c][i]
    #             for index in range(length):
    #                 possible_answer[start_index + index + i] = 2
    #         possible_col_answers = np.vstack((possible_col_answers, possible_answer))
    #     col_answers[c] = possible_col_answers

    # # Intersect Row
    # for r in range(HEIGHT):
    #     line = np.zeros(shape=(WIDTH), dtype=np.int32)

    #     for i in range(WIDTH):
    #         line[i] = row_answers[r][0][i]
    #     for j in range(1, len(row_answers[r])):
    #         for i in range(WIDTH):
    #             if line[i] != row_answers[r][j][i]:
    #                 line[i] = 0

    #     for i in range(WIDTH):
    #         if board[r][i] == 0:
    #             board[r][i] = line[i]
    #         elif line[i] != 0 and board[r][i] != line[i]:
    #             print("ERROR: Illegal constraints")

    # # Intersect Column
    # for c in range(WIDTH):
    #     line = np.zeros(shape=(HEIGHT), dtype=np.int32)
    #     for i in range(HEIGHT):
    #         line[i] = col_answers[c][0][i]
    #     for j in range(1, len(col_answers[c])):
    #         for i in range(HEIGHT):
    #             if line[i] != col_answers[c][j][i]:
    #                 line[i] = 0

    #     for i in range(WIDTH):

    #         if board[i][c] == 0:
    #             board[i][c] = line[i]
    #         elif line[i] != 0 and board[i][c] != line[i]:
    #             print("ERROR: Illegal constraints")
    # print(board)
    # # print("---------------------------------------")
    # # for r in row_answers:
    # #     print(r)
    # # print("---------------------------------------")

    # print("---------------------------------------")
    # for c in col_answers:
    #     print(c)
    # print("---------------------------------------")

    # # With new board, delete impossible answers
    # for r in range(HEIGHT):
    #     for row in reversed(range(len(row_answers[r]))):
    #         # print(row)
    #         answer = row_answers[r][row]
    #         # print(answer)
    #         for i in range(WIDTH):
    #             if board[r][i] != 0 and board[r][i] != answer[i]:
    #                 print(f"delete answer {row} in row {r}")
    #                 row_answers[r] = np.delete(row_answers[r], row, 0)
    #                 break
    #         # print(row)
    # for c in range(WIDTH):
    #     for col in reversed(range(len(col_answers[c]))):
    #         answer = col_answers[c][col]
    #         for i in range(HEIGHT):
    #             if board[i][c] != 0 and board[i][c] != answer[i]:
    #                 print(f"delete answer {col} in col {c}")
    #                 col_answers[c] = np.delete(col_answers[c], col, 0)
    #                 break

    # # print("---------------------------------------")
    # # for r in row_answers:
    # #     print(r)
    # # print("---------------------------------------")

    # print("---------------------------------------")
    # for c in col_answers:
    #     print(c)
    # print("---------------------------------------")

    # print(board)


if __name__ == '__main__':
    main()
