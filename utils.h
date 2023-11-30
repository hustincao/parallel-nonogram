#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

// Board values
#define NOT_SET 9
#define UNFILLED 0
#define FILLED 1
#define UNKNOWN 2

class Game {
  public:
    unsigned int width;
    unsigned int height;
    unsigned int *len_constraints;
    unsigned int **constraints;
    unsigned int num_constraints = 0;

    int **row_answers;
    int **col_answers;

    int **board;
    int **solution;

    void load_game(std::string folder) {
        // Loads constraints
        std::ifstream constraint_file(folder + "/constraints");
        if (constraint_file.is_open()) {
            std::string input_line;
            std::getline(constraint_file, input_line);
            std::stringstream input_stream(input_line);

            input_stream >> width;
            input_stream >> height;

            board = new int *[height];
            solution = new int *[height];
            for (int i = 0; i < height; i++) {
                board[i] = new int[width];
                solution[i] = new int[width];
                for (int j = 0; j < width; j++) {
                    board[i][j] = NOT_SET;
                }
            }

            len_constraints = new unsigned int[width + height];
            constraints = new unsigned int *[width + height];
            col_answers = new int *[width];
            row_answers = new int *[height];

            for (unsigned int i = 0; i < width + height; i++) {
                std::string input_line;
                std::getline(constraint_file, input_line);
                std::stringstream input_stream(input_line);

                int num_groups = 1 + std::count_if(input_line.begin(), input_line.end(),
                                                   [](unsigned char c) { return std::isspace(c); });
                num_constraints += num_groups;
                len_constraints[i] = num_groups;
                constraints[i] = new unsigned int[num_groups];
                for (unsigned int j = 0; j < num_groups; j++) {
                    unsigned int c;
                    input_stream >> c;
                    constraints[i][j] = c;
                }
            }
            constraint_file.close();
        }

        // Load solution
        std::ifstream solution_file(folder + "/solution");
        if (solution_file.is_open()) {
            int i = 0;
            int j = 0;
            while (!solution_file.eof()) {
                char c = solution_file.get();
                if (c != '0' && c != '1')
                    continue;
                solution[i][j] = c - '0';
                j += 1;
                if (j >= width) {
                    i += 1;
                    j = 0;
                }
            }
            solution_file.close();
        }
    };

    void generate_col_answers() {
        for(int i = 0; i < width; i++){
            
        }
    }

    // Compares board to solution
    bool check_solution() {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                if (board[i][j] != solution[i][j]) {
                    return false;
                }
            }
        }
        return true;
    }

    void free_dynamic_memory() {
        for (int i = 0; i < width + height; i++) {
            delete[] constraints[i];
        }
        for (int i = 0; i < width; i++) {
            delete[] col_answers[i];
        }
        for (int i = 0; i < height; i++) {
            delete[] row_answers[i];
            delete[] board[i];
            delete[] solution[i];
        }
        delete[] len_constraints;
        delete[] constraints;
        delete[] board;
        delete[] solution;
    };

    void print_board() {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                std::cout << board[i][j] << " ";
            }
            std::cout << "\n";
        }
    }

    void print_solution() {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                std::cout << solution[i][j] << " ";
            }
            std::cout << "\n";
        }
    }

    void print_constraints() {
        for (int i = 0; i < width + height; i++) {
            for (int j = 0; j < len_constraints[i]; j++) {
                std::cout << constraints[i][j] << " ";
            }
            std::cout << "\n";
        }
    }

    void print_len_constraints() {
        for (unsigned int i = 0; i < width + height; i++) {
            std::cout << len_constraints[i] << "\n";
        }
    }
};
