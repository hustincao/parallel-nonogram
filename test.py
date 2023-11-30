import numpy as np
import time
from multiprocessing import Pool
from threading import Thread, Lock
from itertools import combinations

_UNSET = 5
_UNKNOWN = 4
_UNFILLED = 0
_FILLED = 1


def is_finished(board, HEIGHT, WIDTH):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if board[i][j] == _UNKNOWN:
                return False
    return True

def remove_possible_answers(board, possible_answers, answer_index, is_col):
    for i in reversed(range(len(possible_answers[answer_index]))):
        for index in range(len(possible_answers[answer_index][i])):
            if is_col:
                if board[index, answer_index] != _UNKNOWN and board[index, answer_index] != possible_answers[answer_index][i][index]:
                    possible_answers[answer_index] = np.delete(
                        possible_answers[answer_index], i, 0)
                    # print(f"delete col {answer_index} answer {i}")
                    break
            else:
                if board[answer_index, index] != _UNKNOWN and board[answer_index, index] != possible_answers[answer_index][i][index]:
                    possible_answers[answer_index] = np.delete(
                        possible_answers[answer_index], i, 0)
                    # print(f"delete row {answer_index} answer {i}")
                    break

  

# is_col: True = column, False = row
def intersect_possible_answers(board, possible_answers, answer_index, is_col):
    global isUpdated
    if is_col:
        intersect = np.array(board[:, answer_index], copy=True)
    else:
        intersect = np.array(board[answer_index, :], copy=True)
    
    for _, possible_answer in enumerate(possible_answers[answer_index]):
        for index in range(len(possible_answer)):
            if intersect[index] == _UNKNOWN:
                intersect[index] = possible_answer[index]
            elif intersect[index] != possible_answer[index]:
                intersect[index] = _UNSET
    for i in range(len(intersect)):
        if intersect[i] != _UNSET:
            if is_col:
                if board[i, answer_index] != intersect[i]:
                    isUpdated = True
                board[i, answer_index] = intersect[i]
            else:
                if board[answer_index, i] != intersect[i]:
                    isUpdated = True
                board[answer_index, i] = intersect[i]
    


def generate_combinations(constraints, length, answers, index):
    n_groups = len(constraints)
    n_empty = length - sum(constraints) - n_groups + 1
    opts = list(combinations(range(n_groups+n_empty), n_groups))
    possible_answers = np.full((len(opts), length), _UNFILLED)
    # possible_row_answer = np.full((len(opts),WIDTH), _UNFILLED)
    for opt_index, p in enumerate(opts):
        cumulative_total_length = 0
        for p_index, i in enumerate(p):
            for j in range(cumulative_total_length + i, cumulative_total_length + i + constraints[p_index]):
                possible_answers[opt_index][j] = _FILLED
            cumulative_total_length += constraints[p_index]
    answers[index] = possible_answers

def pool_main(folder, file):
    global isUpdated
    isUpdated = False

    constraint_file = open(f'{folder}/{file}/constraints', 'r')
    lines = constraint_file.readlines()
    HEIGHT, WIDTH = [int(s) for s in lines[0].strip().split()]

    board = np.full((HEIGHT, WIDTH), _UNKNOWN, np.int8)

    solution = np.ndarray(shape=(HEIGHT, WIDTH), dtype=np.int32)
    input_row_constraints = []
    input_col_constraints = []

    for index, line in enumerate(lines[1:]):
        if index < WIDTH:
            input_col_constraints.append(
                [int(s) for s in line.strip().split()])
        else:
            input_row_constraints.append(
                [int(s) for s in line.strip().split()])

    if len(input_col_constraints) != WIDTH or len(input_row_constraints) != HEIGHT:
        print("number of constraints not equal to board size")

    solution_file = open(f'{folder}/{file}/solution', 'r')
    lines = solution_file.readlines()
    for i, line in enumerate(lines):
        for j, value in enumerate(line.strip()):
            solution[i][j] = value

    constraint_file.close()
    solution_file.close()

    row_constraints = np.array([input_row_constraints[i]
                               for i in range(HEIGHT)], dtype=object)
    col_constraints = np.array([input_col_constraints[i]
                               for i in range(WIDTH)], dtype=object)

    possible_row_answers = np.empty(HEIGHT, dtype=object)
    possible_col_answers = np.empty(WIDTH, dtype=object)
    start_time = time.time()

    threads = []

    for r in range(HEIGHT):
        t = Thread(target=generate_combinations, args=(
            row_constraints[r], WIDTH, possible_row_answers, r))
        threads.append(t)
        t.start()
    for c in range(WIDTH):
        t = Thread(target=generate_combinations, args=(
            col_constraints[c], HEIGHT, possible_col_answers, c))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    while True:
        isUpdated = False
        intersect_threads = []
        for r in range(HEIGHT):
            t = Thread(target=intersect_possible_answers, args=(board, possible_row_answers, r, False))
            intersect_threads.append(t)
            t.start()
        for c in range(WIDTH):
            t = Thread(target=intersect_possible_answers, args=(board, possible_col_answers, c, True))
            intersect_threads.append(t)
            t.start()
        for t in intersect_threads:
            t.join()


        remove_possible_answers(board, possible_row_answers, 0, False)

        remove_threads = []
        for r in range(HEIGHT):
            t = Thread(target=remove_possible_answers, args=(board, possible_row_answers, r, False))
            remove_threads.append(t)
            t.start()
        for c in range(WIDTH):
            t = Thread(target=remove_possible_answers, args=(board, possible_col_answers, c, True))
            remove_threads.append(t)
            t.start()
        for t in intersect_threads:
            t.join()

        if is_finished(board, HEIGHT, WIDTH):
            print("finished and correct")
            break
        elif not isUpdated:
            print("Was not updated in last iteration")
            break

    print("%s" % (time.time() - start_time))
    print(board)
    

def parallel_main(folder, file):
    global isUpdated
    isUpdated = False

    constraint_file = open(f'{folder}/{file}/constraints', 'r')
    lines = constraint_file.readlines()
    HEIGHT, WIDTH = [int(s) for s in lines[0].strip().split()]

    board = np.full((HEIGHT, WIDTH), _UNKNOWN, np.int8)

    solution = np.ndarray(shape=(HEIGHT, WIDTH), dtype=np.int32)
    input_row_constraints = []
    input_col_constraints = []

    for index, line in enumerate(lines[1:]):
        if index < WIDTH:
            input_col_constraints.append(
                [int(s) for s in line.strip().split()])
        else:
            input_row_constraints.append(
                [int(s) for s in line.strip().split()])

    if len(input_col_constraints) != WIDTH or len(input_row_constraints) != HEIGHT:
        print("number of constraints not equal to board size")

    solution_file = open(f'{folder}/{file}/solution', 'r')
    lines = solution_file.readlines()
    for i, line in enumerate(lines):
        for j, value in enumerate(line.strip()):
            solution[i][j] = value

    constraint_file.close()
    solution_file.close()

    row_constraints = np.array([input_row_constraints[i]
                               for i in range(HEIGHT)], dtype=object)
    col_constraints = np.array([input_col_constraints[i]
                               for i in range(WIDTH)], dtype=object)

    possible_row_answers = np.empty(HEIGHT, dtype=object)
    possible_col_answers = np.empty(WIDTH, dtype=object)
    start_time = time.time()

    threads = []

    for r in range(HEIGHT):
        t = Thread(target=generate_combinations, args=(
            row_constraints[r], WIDTH, possible_row_answers, r))
        threads.append(t)
        t.start()
    for c in range(WIDTH):
        t = Thread(target=generate_combinations, args=(
            col_constraints[c], HEIGHT, possible_col_answers, c))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    while True:
        isUpdated = False
        intersect_threads = []
        for r in range(HEIGHT):
            t = Thread(target=intersect_possible_answers, args=(board, possible_row_answers, r, False))
            intersect_threads.append(t)
            t.start()
        for c in range(WIDTH):
            t = Thread(target=intersect_possible_answers, args=(board, possible_col_answers, c, True))
            intersect_threads.append(t)
            t.start()
        for t in intersect_threads:
            t.join()


        remove_possible_answers(board, possible_row_answers, 0, False)

        remove_threads = []
        for r in range(HEIGHT):
            t = Thread(target=remove_possible_answers, args=(board, possible_row_answers, r, False))
            remove_threads.append(t)
            t.start()
        for c in range(WIDTH):
            t = Thread(target=remove_possible_answers, args=(board, possible_col_answers, c, True))
            remove_threads.append(t)
            t.start()
        for t in intersect_threads:
            t.join()

        if is_finished(board, HEIGHT, WIDTH):
            print("finished and correct")
            break
        elif not isUpdated:
            print("Was not updated in last iteration")
            break

    print("%s" % (time.time() - start_time))
    print(board)

def main(folder, file):
    global isUpdated
    

    constraint_file = open(f'{folder}/{file}/constraints', 'r')
    lines = constraint_file.readlines()
    HEIGHT, WIDTH = [int(s) for s in lines[0].strip().split()]

    board = np.full((HEIGHT, WIDTH), _UNKNOWN, np.int8)
   
    solution = np.ndarray(shape=(HEIGHT, WIDTH), dtype=np.int32)
    input_row_constraints = []
    input_col_constraints = []

    for index, line in enumerate(lines[1:]):
        if index < WIDTH:
            input_col_constraints.append(
                [int(s) for s in line.strip().split()])
        else:
            input_row_constraints.append(
                [int(s) for s in line.strip().split()])

    if len(input_col_constraints) != WIDTH or len(input_row_constraints) != HEIGHT:
        print("number of constraints not equal to board size")

    solution_file = open(f'{folder}/{file}/solution', 'r')
    lines = solution_file.readlines()
    for i, line in enumerate(lines):
        for j, value in enumerate(line.strip()):
            solution[i][j] = value

    constraint_file.close()
    solution_file.close()

    row_constraints = np.array([input_row_constraints[i]
                               for i in range(HEIGHT)], dtype=object)
    col_constraints = np.array([input_col_constraints[i]
                               for i in range(WIDTH)], dtype=object)

    possible_row_answers = np.empty(HEIGHT, dtype=object)
    possible_col_answers = np.empty(WIDTH, dtype=object)
    start_time = time.time()

    for r in range(HEIGHT):
        n_groups = len(row_constraints[r])
        n_empty = WIDTH - sum(row_constraints[r]) - n_groups + 1
        opts = list(combinations(range(n_groups+n_empty), n_groups))
        possible_row_answer = np.full((len(opts), WIDTH), _UNFILLED)
        for opt_index, p in enumerate(opts):
            cumulative_total_length = 0
            for p_index, i in enumerate(p):
                for j in range(cumulative_total_length + i, cumulative_total_length + i + row_constraints[r][p_index]):
                    possible_row_answer[opt_index][j] = _FILLED
                cumulative_total_length += row_constraints[r][p_index]
        possible_row_answers[r] = possible_row_answer

    for c in range(WIDTH):
        n_groups = len(col_constraints[c])
        n_empty = HEIGHT - sum(col_constraints[c]) - n_groups + 1
        opts = list(combinations(range(n_groups+n_empty), n_groups))
        possible_col_answer = np.full((len(opts), HEIGHT), _UNFILLED)
        for opt_index, p in enumerate(opts):
            cumulative_total_length = 0
            for p_index, i in enumerate(p):
                for j in range(cumulative_total_length + i, cumulative_total_length + i + col_constraints[c][p_index]):
                    possible_col_answer[opt_index][j] = _FILLED
                cumulative_total_length += col_constraints[c][p_index]
        possible_col_answers[c] = possible_col_answer

    while True:
        isUpdated = False
        for r in range(HEIGHT):
            intersect = np.array(board[r, :], copy=True)
            for _, possible_row_answer in enumerate(possible_row_answers[r]):
                for index in range(WIDTH):
                    if intersect[index] == _UNKNOWN:
                        intersect[index] = possible_row_answer[index]
                    elif intersect[index] != possible_row_answer[index]:
                        intersect[index] = _UNSET
            for i in range(WIDTH):
                if intersect[i] != _UNSET:
                    if board[r, i] != intersect[i]:
                        isUpdated = True
                    board[r, i] = intersect[i]

        for c in range(WIDTH):
            intersect = np.array(board[:, c], copy=True)
            for _, possible_col_answer in enumerate(possible_col_answers[c]):
                for index in range(HEIGHT):
                    if intersect[index] == _UNKNOWN:
                        intersect[index] = possible_col_answer[index]
                    elif intersect[index] != possible_col_answer[index]:
                        intersect[index] = _UNSET
            for i in range(HEIGHT):
                if intersect[i] != _UNSET:
                    if board[i, c] != intersect[i]:
                        isUpdated = True
                    board[i, c] = intersect[i]

        for r in range(HEIGHT):
            for i in reversed(range(len(possible_row_answers[r]))):
                for index in range(WIDTH):
                    if board[r, index] != _UNKNOWN and board[r, index] != possible_row_answers[r][i][index]:
                        possible_row_answers[r] = np.delete(
                            possible_row_answers[r], i, 0)
                        # print(f"delete row {r} answer {i}")
                        break

        for c in range(WIDTH):
            for i in reversed(range(len(possible_col_answers[c]))):
                for index in range(HEIGHT):
                    if board[index, c] != _UNKNOWN and board[index, c] != possible_col_answers[c][i][index]:
                        possible_col_answers[c] = np.delete(
                            possible_col_answers[c], i, 0)
                        # print(f"delete col {c} answer {i}")
                        break

        if is_finished(board, HEIGHT, WIDTH):
            print("finished and correct")
            break
        elif not isUpdated:
            print("Was not updated in last iteration")

    print("%s" % (time.time() - start_time))
    print(board)


if __name__ == '__main__':
    folder = 'created-tests'
    file = '20x20'
    main(folder, file)
    parallel_main(folder, file)
    print("end program")
