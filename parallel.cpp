#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <chrono>
#include <omp.h>


using namespace std;
typedef std::chrono::high_resolution_clock Clock;

#define THREAD_NUM 4
#define UNKNOWN 4
#define UNFILLED 0
#define FILLED 1
void print_board(vector<vector<int>> board) {
    for (int i = 0; i < board.size(); i++) {
        for (int j = 0; j < board[i].size(); j++) {
            cout << board[i][j] << " ";
        }
        cout << "\n";
    }
}
void print_all_possible_answers(vector<vector<int>> all_possible_answers) {
    cout << "--------------\n";
    for (int i = 0; i < all_possible_answers.size(); i++) {
        for (int j = 0; j < all_possible_answers[i].size(); j++) {
            cout << all_possible_answers[i][j] << " ";
        }
        cout << "\n";
    }
    cout << "--------------\n";
}
void generate_possible_answers_helper(vector<vector<int>> &all_possible_answers, vector<int> constraints, vector<int> possible_answer, int constraint_index, int answer_index) {
    if (constraint_index >= constraints.size()) {
        all_possible_answers.push_back(possible_answer);
        return;
    }
    if (answer_index >= possible_answer.size()) {
        return;
    }

    if (answer_index + constraints[constraint_index] < possible_answer.size() + 1) {
        vector<int> possible_answer_2(possible_answer);
        for (int i = answer_index; i < answer_index + constraints[constraint_index]; i++) {
            possible_answer_2[i] = FILLED;
        }

        generate_possible_answers_helper(all_possible_answers, constraints, vector<int>(possible_answer_2), constraint_index + 1, answer_index + constraints[constraint_index] + 1);
    }

    generate_possible_answers_helper(all_possible_answers, constraints, vector<int>(possible_answer), constraint_index, answer_index + 1);
}
// Generates constraints for a line and returns a 2D vector with all possible answers.
vector<vector<int>> generate_all_possible_answers(vector<int> constraints, int length) {

    vector<vector<int>> all_possible_answers;
    vector<int> start(length);
    std::fill_n(start.begin(), start.size(), UNFILLED);

    generate_possible_answers_helper(all_possible_answers, constraints, start, 0, 0);

    return all_possible_answers;
}

void intersect_all_possible_answers(vector<vector<int>> all_possible_answers, int length, vector<vector<int>> &board, int index, bool is_column) {
    // Fill intersection with first answer
    vector<int> intersection(all_possible_answers[0]);
    for (int i = 1; i < all_possible_answers.size(); i++) {
        for (int j = 0; j < length; j++) {
            if (intersection[j] != all_possible_answers[i][j]) {
                intersection[j] = UNKNOWN;
            }
        }
    }

    // cout << (is_column ? "col" : "row") << " " << index << "\n";
    // for(int i = 0; i < length; i++){
    //     cout << intersection[i] << " ";
    // }
    // cout << "\n";
    // print_all_possible_answers(all_possible_answers);
    // cout << "-----------\n";
   
    // Set board
    if (is_column) {
        for (int i = 0; i < length; i++) {
            if (board[i][index] == UNKNOWN) {
                board[i][index] = intersection[i];
            } else if (intersection[i] != UNKNOWN && board[i][index] != intersection[i]) {
                cout << board[i][index] << " " << intersection[i] << '\n';
                cout << "Error at col " << index << " row " << i << "\n";
            }
        }
    } else {
        for (int i = 0; i < length; i++) {
            if (board[index][i] == UNKNOWN) {
                board[index][i] = intersection[i];
            } else if (intersection[i] != UNKNOWN && board[index][i] != intersection[i]) {
                cout << board[index][i] << " " << intersection[i] << '\n';
                cout << "Error at row " << index << " col " << i << "\n";
            }
        }
    }
}

bool remove_possible_answers(vector<vector<int>> &all_possible_answers, int length, vector<vector<int>> board, int index, bool is_column) {

    bool is_updated = false;
    if (is_column) {
        for (int i = all_possible_answers.size() - 1; i >= 0; i--) {
            for (int j = 0; j < length; j++) {
                if (board[j][index] != UNKNOWN && board[j][index] != all_possible_answers[i][j]) {
                    all_possible_answers.erase(all_possible_answers.begin() + i);
                    is_updated = true;
                    break;
                }
            }
        }
    } else {
        for (int i = all_possible_answers.size() - 1; i >= 0; i--) {
            for (int j = 0; j < length; j++) {            
                if (board[index][j] != UNKNOWN && board[index][j] != all_possible_answers[i][j]) {
                    all_possible_answers.erase(all_possible_answers.begin() + i);
                    is_updated = true;
                    break;
                }
            }
        }
    }
    return is_updated;
}

bool is_finished(vector<vector<int>> board) {
    for (int i = 0; i < board.size(); i++) {
        for (int j = 0; j < board[i].size(); j++) {
            if (board[i][j] == UNKNOWN) {
                return false;
            }
        }
    }
    return true;
}
bool is_correct(vector<vector<int>> board, vector<vector<int>> solution) {
    for (int i = 0; i < board.size(); i++) {
        for (int j = 0; j < board[i].size(); j++) {
            if (board[i][j] != solution[i][j]) {
                return false;
            }
        }
    }
    return true;
}

int main() {
    // omp_set_thread_num(THREAD_NUM);
    omp_set_num_threads(THREAD_NUM);
    #pragma omp parallel
    {
        if(omp_get_thread_num() == 0){
            cout << "Running with " << omp_get_num_threads() << " threads\n";
        }
    }
    
    string parent_folder = "tests/tiny";
    string test_folder = "65956";
#pragma region
    int WIDTH;
    int HEIGHT;
    

    vector<vector<int>> row_constraints;
    vector<vector<int>> col_constraints;

   
    ifstream constraint_file(parent_folder + "/" + test_folder + "/constraints");
    if (constraint_file.is_open()) {
        std::string input_line;
        std::getline(constraint_file, input_line);
        std::stringstream input_stream(input_line);

        input_stream >> WIDTH;
        input_stream >> HEIGHT;

        for (int i = 0; i < WIDTH; i++) {
            vector<int> constraints;
            std::getline(constraint_file, input_line);
            std::stringstream input_stream(input_line);
            int s = 0;
            while (input_stream >> s) {
                constraints.push_back(s);
            }
            col_constraints.push_back(constraints);
        }

        for (int i = 0; i < HEIGHT; i++) {
            vector<int> constraints;
            std::getline(constraint_file, input_line);
            std::stringstream input_stream(input_line);
            int s = 0;
            while (input_stream >> s) {
                constraints.push_back(s);
            }
            row_constraints.push_back(constraints);
        }
    }
    constraint_file.close();
    vector<vector<int>> solution(HEIGHT, vector<int>(WIDTH, UNKNOWN));

    ifstream solution_file(parent_folder + "/" + test_folder + "/solution");
    if (solution_file.is_open()) {
        int i = 0;
        int j = 0;
        while (!solution_file.eof()) {
            char c = solution_file.get();
            if (c != '0' && c != '1')
                continue;
            solution[i][j] = c - '0';
            j += 1;
            if (j >= WIDTH) {
                i += 1;
                j = 0;
            }
        }
        solution_file.close();
    }

    // for (int i = 0; i < row_constraints.size(); i++) {
    //     for (int j = 0; j < row_constraints[i].size(); j++) {
    //         cout << row_constraints[i][j] << " ";
    //     }
    //     cout << '\n';
    // }

    // for (int i = 0; i < col_constraints.size(); i++) {
    //     for (int j = 0; j < col_constraints[i].size(); j++) {
    //         cout << col_constraints[i][j] << " ";
    //     }
    //     cout << '\n';
    // }

    vector<vector<int>> board(HEIGHT, vector<int>(WIDTH, UNKNOWN));
#pragma endregion

    vector<vector<vector<int>>> all_possible_row_answers(HEIGHT);
    vector<vector<vector<int>>> all_possible_col_answers(WIDTH);

    auto start_generation = Clock::now();
    
    #pragma omp parallel for
    for (int i = 0; i < HEIGHT; i++) {
        all_possible_row_answers[i] = generate_all_possible_answers(row_constraints[i], WIDTH);
        // cout << "row " << i << "\n";
        // print_all_possible_answers(all_possible_row_answers[i]);
    }

    #pragma omp parallel for
    for (int i = 0; i < WIDTH; i++) {
        all_possible_col_answers[i] = generate_all_possible_answers(col_constraints[i], HEIGHT);
        // cout << "col " << i << "\n";
        // print_all_possible_answers(all_possible_col_answers[i]);
    }
    auto end_generation = Clock::now();
    std::cout << "Generation:"
      << std::chrono::duration_cast<std::chrono::microseconds>(end_generation - start_generation).count() << " microseconds\n";
    bool is_updated = false;
    auto start_solver = Clock::now();
    while (true) {
        is_updated = false;
        #pragma omp parallel for
        for (int i = 0; i < HEIGHT; i++) {
            intersect_all_possible_answers(all_possible_row_answers[i], WIDTH, board, i, false);
        }
        #pragma omp parallel for
        for (int i = 0; i < WIDTH; i++) {
            intersect_all_possible_answers(all_possible_col_answers[i], HEIGHT, board, i, true);
        }
        #pragma omp parallel for
        for (int i = 0; i < HEIGHT; i++) {
            bool update = remove_possible_answers(all_possible_row_answers[i], WIDTH, board, i, false);

            is_updated = is_updated || update;
        }
        #pragma omp parallel for
        for (int i = 0; i < WIDTH; i++) {
            bool update = remove_possible_answers(all_possible_col_answers[i], HEIGHT, board, i, true);
      
            is_updated = is_updated || update;
        }

        if (is_finished(board)) {
            // cout << "finished board\n";
            break;
        }
        if (!is_updated) {
            break;
        }
    }
    auto end_solver = Clock::now();
    std::cout << "Solver:"
      << std::chrono::duration_cast<std::chrono::microseconds>(end_solver - start_solver).count() << " microseconds\n";
    cout << "is correct: " << is_correct(board, solution) << "\n";
    return 0;
}