#include "utils.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

// Board state for each cell
enum State { NOT_SET = -1,
             UNFILLED = 0,
             FILLED = 1 };

int main() {
    // std::cout << "Start Program\n";
    // std::ifstream constraint_file("tests/0/constraints");
    Board board;

    board.load_board("tests/0/constraints");

    std::cout << board.width << " " << board.height << "\n";

    std::cout << "----------------------\n";

    for (int i = 0; i < board.width + board.height; i++) {
        for (int j = 0; j < board.len_constraints[i]; j++) {
            std::cout << board.constraints[i][j] << " ";
        }
        std::cout << "\n";
    }
    std::cout << "----------------------\n";
    for (unsigned int i = 0; i < board.width + board.height; i++) {
        std::cout << board.len_constraints[i] << "\n";
    }

    board.delete_dynamic_memory();

    // if (constraint_file.is_open()) {
    //     // Reads the width and height of the board
    //     std::string input_line;
    //     std::getline(constraint_file, input_line);
    //     std::stringstream input_stream(input_line);

    //     input_stream >> width;
    //     input_stream >> height;
    //     len_constraints = new unsigned int[width + height];
    //     constraints = new unsigned int *[width + height];

    //     // Load board
    //     std::cout << width << " " << height << "\n";
    //     for (unsigned int i = 0; i < width + height; i++) {
    //         std::string input_line;
    //         std::getline(constraint_file, input_line);
    //         std::stringstream input_stream(input_line);

    //         int num_groups = 1 + std::count_if(input_line.begin(), input_line.end(),
    //                                            [](unsigned char c) { return std::isspace(c); });
    //         len_constraints[i] = num_groups;
    //         constraints[i] = new unsigned int[num_groups];
    //         for (unsigned int j = 0; j < num_groups; j++) {
    //             unsigned int c;
    //             input_stream >> c;
    //             constraints[i][j] = c;
    //         }
    //     }
    //     constraint_file.close();

    //     std::cout << "----------------------\n";

    //     for (int i = 0; i < width + height; i++) {
    //         for (int j = 0; j < len_constraints[i]; j++) {
    //             std::cout << constraints[i][j] << " ";
    //         }
    //         std::cout << "\n";
    //     }
    //     std::cout << "----------------------\n";
    //     for (unsigned int i = 0; i < width + height; i++) {
    //         std::cout << len_constraints[i] << "\n";
    //     }

    //     // Delete dynamic memory
    //     for (int i = 0; i < width + height; i++) {
    //         delete[] constraints[i];
    //     }
    //     delete[] len_constraints;
    //     delete[] constraints;
    // }

    return 0;
}