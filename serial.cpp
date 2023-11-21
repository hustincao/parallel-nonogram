#include "utils.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

bool can_place_block(int *arr, int arr_len, int start_index, int block_len) {
    // Check boundaries
    if (start_index < 0 || start_index + block_len > arr_len)
        return false;
    // Check if cell before index is set to black
    if (start_index > 0 && arr[start_index - 1] == FILLED)
        return false;
    // Check if cell after index is set to black
    if (start_index + block_len < arr_len - 1 && arr[start_index + block_len] == FILLED)
        return false;
    // Check inbetween
    for (int i = start_index; i < start_index + block_len; i++) {
        if (arr[i] == UNFILLED)
            return false;
    }
    return true;
}

void update_cell(int *arr, int index, int color) {
    if (arr[index] == NOT_SET) // If the cell is unset, we can set it to the color.
        arr[index] = color;
    else if (arr[index] != color) // If the cell is set to a different color, then we can set it to either color
        arr[index] = UNKNOWN;
}

void place_block(int *arr, int start_index, int block_len) {
    if (start_index > 0)
        update_cell(arr, start_index - 1, UNFILLED);
    // arr[start_index - 1] = UNFILLED;
    if (start_index + block_len)
        update_cell(arr, start_index + block_len, UNFILLED);
    // arr[start_index + block_len] = UNFILLED;
    for (int i = start_index; i < start_index + block_len; i++) {
        update_cell(arr, i, FILLED);
    }
}

void solve_block(int *arr, int arr_len, unsigned int constraint, unsigned int left_index, unsigned int right_index) {
    // std::cout << left_index << ", " << right_index << "\n";
    int *solved_line = new int[arr_len];
    for (int i = 0; i < arr_len; i++) {
        solved_line[i] = arr[i];
        // std::cout << solved_line[i] << " ";
    }
    // std::cout << "\n";
    for (unsigned int i = left_index; i < right_index - constraint + 1; i++) {
        // Place block
        // std::cout << i << "\n";
        if (can_place_block(arr, arr_len, i, constraint)) {
            // std::cout << i << "\n";
            place_block(solved_line, i, constraint);
        }
    }
    for (int i = left_index; i < right_index; i++) {
        // std::cout << solved_line[i] << " ";
        if (solved_line[i] == FILLED || solved_line[i] == UNFILLED)
            arr[i] = solved_line[i];
    }
    // std::cout << "\n";
    delete[] solved_line;
}

void solve_line(int *arr, int arr_len, unsigned int *constraints, unsigned int constraint_len) {
    for (unsigned int i = 0; i < constraint_len; i++) {
        unsigned int left_index = i;
        unsigned int right_index = arr_len - constraint_len + i + 1;
        for (unsigned int j = 0; j < i; j++) {
            left_index += constraints[j];
        }
        for (unsigned int j = i + 1; j < constraint_len; j++) {
            right_index -= constraints[j];
        }
        // std::cout << left_index << " " << right_index << "\n";
        solve_block(arr, arr_len, constraints[i], left_index, right_index);
    }
}

int main() {
    Game game;

    game.load_game("tests/0");

    // Solve columns
    for (unsigned int i = 0; i < game.width; i++) {
        int *arr = new int[game.height];

        for (unsigned int j = 0; j < game.height; j++) {
            arr[j] = game.board[j][i];
        }

        solve_line(arr, game.height, game.constraints[i], game.len_constraints[i]);

        for (unsigned int j = 0; j < game.height; j++) {
            game.board[j][i] = arr[j];
            // std::cout << arr[j] << " ";
        }
        // std::cout << "\n";

        delete[] arr;
    }
    // Solve rows
    for (unsigned int i = 0; i < game.height; i++) {
        int *arr = new int[game.width];

        for (unsigned int j = 0; j < game.width; j++) {
            arr[j] = game.board[i][j];
        }

        solve_line(arr, game.width, game.constraints[i + game.width], game.len_constraints[i + game.width]);

        for (unsigned int j = 0; j < game.width; j++) {
            game.board[i][j] = arr[j];
            // std::cout << arr[j] << " ";
        }
        // std::cout << "\n";

        delete[] arr;
    }
    
    game.print_board();
    std::cout<< "---------------------------------\n";
    game.print_solution();
    game.free_dynamic_memory();

    return 0;
}
