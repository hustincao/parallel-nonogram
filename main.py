import sys
# from numba import cuda
import multiprocessing as mp
from multiprocessing import Queue, Process, cpu_count, Pool
import numpy as np
from itertools import combinations
import time

UNFILLED = 0  # White
FILLED = 1  # Black
UNKNOWN = 6

def parallel_generate_row_possibilities(HEIGHT, WIDTH, ROW_CONSTRAINTS, row_answers, r):
    # Generate all possible row answers
    # for r in range(HEIGHT):
    n_groups = len(ROW_CONSTRAINTS[r])
    n_empty = WIDTH - sum(ROW_CONSTRAINTS[r]) - n_groups + 1
    possible_row_answers = np.ndarray(shape=(0, WIDTH), dtype=np.int32)
    for p in combinations(range(n_groups + n_empty), n_groups):
        possible_answer = np.full(
            shape=(WIDTH), fill_value=UNFILLED, dtype=np.int32)
        total_sum = 0
        for i in range(len(p)):
            start_index = total_sum + p[i]
            length = ROW_CONSTRAINTS[r][i]
            for index in range(length):
                possible_answer[start_index + index] = FILLED
            total_sum += length
        possible_row_answers = np.vstack(
            (possible_row_answers, possible_answer))
        
    # return possible_row_answers
    row_answers[r] = possible_row_answers

def parallel_generate_col_possibilities(HEIGHT, WIDTH, COL_CONSTRAINTS, col_answers, c):
    n_groups = len(COL_CONSTRAINTS[c])
    n_empty = HEIGHT - sum(COL_CONSTRAINTS[c]) - n_groups + 1
    possible_col_answers = np.ndarray(shape=(0, HEIGHT), dtype=np.int32)
    for p in combinations(range(n_groups + n_empty), n_groups):
        possible_answer = np.full(
            shape=(HEIGHT), fill_value=UNFILLED, dtype=np.int32)
        total_sum = 0
        for i in range(len(p)):
            start_index = total_sum + p[i]
            length = COL_CONSTRAINTS[c][i]
            for index in range(length):
                possible_answer[start_index + index] = FILLED
            total_sum += length

        possible_col_answers = np.vstack(
            (possible_col_answers, possible_answer))
    col_answers[c] = possible_col_answers

def parallel_intersect_row_possibilities(HEIGHT, WIDTH, row_answers, board, r):
    line = np.full(shape=(WIDTH), fill_value=UNKNOWN, dtype=np.int32)

    for i in range(WIDTH):
        line[i] = row_answers[r][0][i]
    for j in range(1, len(row_answers[r])):
        for i in range(WIDTH):
            if line[i] != row_answers[r][j][i]:
                line[i] = UNKNOWN
    for i in range(WIDTH):
        if board[r][i] == UNKNOWN:
            board[r][i] = line[i]
        elif line[i] != UNKNOWN and board[r][i] != line[i]:
            print("ERROR: Illegal constraints")
    # board[r] = line
    


def parallel_intersect_col_possibilities(HEIGHT, WIDTH, col_answers, board, c):
    line = np.full(shape=(HEIGHT), fill_value=UNKNOWN, dtype=np.int32)
    for i in range(HEIGHT):
        line[i] = col_answers[c][0][i]
    for j in range(1, len(col_answers[c])):
        for i in range(HEIGHT):
            if line[i] != col_answers[c][j][i]:
                line[i] = UNKNOWN

    for i in range(WIDTH):
        if board[i][c] == UNKNOWN:
            board[i][c] = line[i]
        elif line[i] != UNKNOWN and board[i][c] != line[i]:
            print("ERROR: Illegal constraints")

def parallel_remove_row_possibilities(HEIGHT, WIDTH, row_answers, board, r):
    for row in reversed(range(len(row_answers[r]))):
        answer = row_answers[r][row]
        for i in range(WIDTH):
            if board[r][i] != UNKNOWN and board[r][i] != answer[i]:
                # print(f"delete answer {row} in row {r}")
                row_answers[r] = np.delete(row_answers[r], row, 0)
                break


def parallel_remove_col_possibilities(HEIGHT, WIDTH, col_answers, board, c):
    for col in reversed(range(len(col_answers[c]))):
        answer = col_answers[c][col]
        for i in range(HEIGHT):
            if board[i][c] != UNKNOWN and board[i][c] != answer[i]:
                # print(f"delete answer {col} in col {c}")
                col_answers[c] = np.delete(col_answers[c], col, 0)
                break

def generate_row_possibilities(HEIGHT, WIDTH, ROW_CONSTRAINTS, row_answers):
    # Generate all possible row answers
    for r in range(HEIGHT):
        n_groups = len(ROW_CONSTRAINTS[r])
        n_empty = WIDTH - sum(ROW_CONSTRAINTS[r]) - n_groups + 1
        possible_row_answers = np.ndarray(shape=(0, WIDTH), dtype=np.int32)
        for p in combinations(range(n_groups + n_empty), n_groups):
            possible_answer = np.full(
                shape=(WIDTH), fill_value=UNFILLED, dtype=np.int32)
            total_sum = 0
            for i in range(len(p)):
                start_index = total_sum + p[i]
                length = ROW_CONSTRAINTS[r][i]
                for index in range(length):
                    possible_answer[start_index + index] = FILLED
                total_sum += length
            possible_row_answers = np.vstack(
                (possible_row_answers, possible_answer))
        row_answers[r] = possible_row_answers


def generate_col_possibilities(HEIGHT, WIDTH, COL_CONSTRAINTS, col_answers):
    for c in range(WIDTH):
        n_groups = len(COL_CONSTRAINTS[c])
        n_empty = HEIGHT - sum(COL_CONSTRAINTS[c]) - n_groups + 1
        possible_col_answers = np.ndarray(shape=(0, HEIGHT), dtype=np.int32)
        for p in combinations(range(n_groups + n_empty), n_groups):
            possible_answer = np.full(
                shape=(HEIGHT), fill_value=UNFILLED, dtype=np.int32)
            total_sum = 0
            for i in range(len(p)):
                start_index = total_sum + p[i]
                length = COL_CONSTRAINTS[c][i]
                for index in range(length):
                    possible_answer[start_index + index] = FILLED
                total_sum += length

            possible_col_answers = np.vstack(
                (possible_col_answers, possible_answer))
        col_answers[c] = possible_col_answers


def intersect_row_possibilities(HEIGHT, WIDTH, row_answers, board):
    for r in range(HEIGHT):
        line = np.full(shape=(WIDTH), fill_value=UNKNOWN, dtype=np.int32)

        for i in range(WIDTH):
            line[i] = row_answers[r][0][i]
        for j in range(1, len(row_answers[r])):
            for i in range(WIDTH):
                if line[i] != row_answers[r][j][i]:
                    line[i] = UNKNOWN

        for i in range(WIDTH):
            if board[r][i] == UNKNOWN:
                board[r][i] = line[i]
            elif line[i] != UNKNOWN and board[r][i] != line[i]:
                print("ERROR: Illegal constraints")


def intersect_col_possibilities(HEIGHT, WIDTH, col_answers, board):
    for c in range(WIDTH):
        line = np.full(shape=(HEIGHT), fill_value=UNKNOWN, dtype=np.int32)
        for i in range(HEIGHT):
            line[i] = col_answers[c][0][i]
        for j in range(1, len(col_answers[c])):
            for i in range(HEIGHT):
                if line[i] != col_answers[c][j][i]:
                    line[i] = UNKNOWN

        for i in range(WIDTH):
            if board[i][c] == UNKNOWN:
                board[i][c] = line[i]
            elif line[i] != UNKNOWN and board[i][c] != line[i]:
                print("ERROR: Illegal constraints")


def remove_row_possibilities(HEIGHT, WIDTH, row_answers, board):
    for r in range(HEIGHT):
        for row in reversed(range(len(row_answers[r]))):
            answer = row_answers[r][row]
            for i in range(WIDTH):
                if board[r][i] != UNKNOWN and board[r][i] != answer[i]:
                    # print(f"delete answer {row} in row {r}")
                    row_answers[r] = np.delete(row_answers[r], row, 0)
                    break


def remove_col_possibilities(HEIGHT, WIDTH, col_answers, board):
    for c in range(WIDTH):
        for col in reversed(range(len(col_answers[c]))):
            answer = col_answers[c][col]
            for i in range(HEIGHT):
                if board[i][c] != UNKNOWN and board[i][c] != answer[i]:
                    # print(f"delete answer {col} in col {c}")
                    col_answers[c] = np.delete(col_answers[c], col, 0)
                    break


def is_completed(HEIGHT, WIDTH, board):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if board[i][j] == UNKNOWN:
                return False
    return True


def is_correct(HEIGHT, WIDTH, board, solution):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if board[i][j] != solution[i][j]:
                return False
    return True

def parallel_main():
    # folder = 'created-tests'
    # files=['0','1','2', '3', '4',]
    # files= [ '5', '6', '7', '8', '9', '10']
    folder='paper-test'
    files = ['boy-skiing',  'mushroom', 'snowman-skiing', 'hunter',]


    for file in files:
        print(file)

        start_time = time.time()
        ROW_CONSTRAINTS = []
        COL_CONSTRAINTS = []

        # filename = 'paper-test/mushroom'

        constraint_file = open(f'{folder}/{file}/constraints', 'r')
        lines = constraint_file.readlines()
        HEIGHT, WIDTH = [int(s) for s in lines[0].strip().split()]
        for index, line in enumerate(lines[1:]):
            if index < HEIGHT:
                COL_CONSTRAINTS.append([int(s) for s in line.strip().split()])
            else:
                ROW_CONSTRAINTS.append([int(s) for s in line.strip().split()])

        if len(COL_CONSTRAINTS) != WIDTH or len(ROW_CONSTRAINTS) != HEIGHT:
            print("number of constraints not equal to board size")
            sys.exit()

        solution = np.ndarray(shape=(HEIGHT, WIDTH), dtype=np.int32)

        solution_file = open(f'{folder}/{file}/solution', 'r')
        lines = solution_file.readlines()
        for i, line in enumerate(lines):
            for j, value in enumerate(line.strip()):
                solution[i][j] = value

        constraint_file.close()
        solution_file.close()

        manager = mp.Manager()
        board = manager.dict()
        for r in range(HEIGHT):
            board[r] = manager.dict()
            for c in range(WIDTH):
                board[r][c] = UNKNOWN

        row_answers = manager.dict()
        col_answers = manager.dict()

        generate_processes = []
        for r in range(HEIGHT):
            p = Process(target=parallel_generate_row_possibilities, args=(HEIGHT, WIDTH, ROW_CONSTRAINTS, row_answers, r))
            generate_processes.append(p)
            p.start()
        
        for c in range(WIDTH):
            p = Process(target=parallel_generate_col_possibilities, args=(HEIGHT, WIDTH, COL_CONSTRAINTS, col_answers, c))
            generate_processes.append(p)
            p.start()

        for p in generate_processes:
            p.join()

        counter = 0
        
        while True:
            intersect_processes = []
            for r in range(HEIGHT):
                p = Process(target=parallel_intersect_row_possibilities, args=(HEIGHT, WIDTH, row_answers, board, r))
                intersect_processes.append(p)
                p.start()
            
            for c in range(WIDTH):
                p = Process(target=parallel_intersect_col_possibilities, args=(HEIGHT, WIDTH, col_answers, board, c))
                intersect_processes.append(p)
                p.start()

            for p in intersect_processes:
                p.join()
       

            remove_processes = []
            for r in range(HEIGHT):
                p = Process(target=parallel_remove_row_possibilities, args=(HEIGHT, WIDTH, row_answers, board, r))
                remove_processes.append(p)
                p.start()
            
            for c in range(WIDTH):
                p = Process(target=parallel_remove_col_possibilities, args=(HEIGHT, WIDTH, col_answers, board, c))
                remove_processes.append(p)
                p.start()

            for p in remove_processes:
                p.join()

            counter += 1

            if is_completed(HEIGHT, WIDTH, board) or counter > 10:
                break
            
        print(is_correct(HEIGHT, WIDTH, board, solution))
        print("%s" % (time.time() - start_time))


def main():
    # folder = 'created-tests'
    # files=['0','1','2', '3', '4',]
    # files= [ '5', '6', '7', '8', '9', '10']
    folder='paper-test'
    files = ['boy-skiing',  'mushroom', 'snowman-skiing', 'hunter',]

    for file in files:
        print(file)

        start_time = time.time()
        ROW_CONSTRAINTS = []
        COL_CONSTRAINTS = []

        # filename = 'paper-test/mushroom'

        constraint_file = open(f'{folder}/{file}/constraints', 'r')
        lines = constraint_file.readlines()
        HEIGHT, WIDTH = [int(s) for s in lines[0].strip().split()]
        for index, line in enumerate(lines[1:]):
            if index < HEIGHT:
                COL_CONSTRAINTS.append([int(s) for s in line.strip().split()])
            else:
                ROW_CONSTRAINTS.append([int(s) for s in line.strip().split()])

        if len(COL_CONSTRAINTS) != WIDTH or len(ROW_CONSTRAINTS) != HEIGHT:
            print("number of constraints not equal to board size")
            sys.exit()

        solution = np.ndarray(shape=(HEIGHT, WIDTH), dtype=np.int32)

        solution_file = open(f'{folder}/{file}/solution', 'r')
        lines = solution_file.readlines()
        for i, line in enumerate(lines):
            for j, value in enumerate(line.strip()):
                solution[i][j] = value

        constraint_file.close()
        solution_file.close()

        board = np.full(shape=(HEIGHT, WIDTH), dtype=np.int32,
                        fill_value=[UNKNOWN for _ in range(HEIGHT)])

        row_answers = np.full(shape=(HEIGHT), fill_value=[
                            _ for _ in range(HEIGHT)], dtype=np.dtype(object))
        col_answers = np.full(shape=(WIDTH), fill_value=[
                            _ for _ in range(WIDTH)], dtype=np.dtype(object))

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

        print(is_correct(HEIGHT, WIDTH, board, solution))
        
        print("%s" % (time.time() - start_time))



if __name__ == '__main__':
    # parallel_main()
    main()
