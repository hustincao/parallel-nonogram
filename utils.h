#include <algorithm>
#include <fstream>
#include <sstream>
#include <string>

class Board {
    public:
        unsigned int width;
        unsigned int height;
        unsigned int *len_constraints;
        unsigned int **constraints;

        void load_board(std::string filename) {
            std::ifstream constraint_file(filename);
            if (constraint_file.is_open()) {
                std::string input_line;
                std::getline(constraint_file, input_line);
                std::stringstream input_stream(input_line);

                input_stream >> width;
                input_stream >> height;

                len_constraints = new unsigned int[width + height];
                constraints = new unsigned int *[width + height];

                // Load board
                for (unsigned int i = 0; i < width + height; i++) {
                    std::string input_line;
                    std::getline(constraint_file, input_line);
                    std::stringstream input_stream(input_line);

                    int num_groups = 1 + std::count_if(input_line.begin(), input_line.end(),
                                                    [](unsigned char c) { return std::isspace(c); });
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
        };

        void delete_dynamic_memory() {
            for (int i = 0; i < width + height; i++) {
                delete[] constraints[i];
            }
            delete[] len_constraints;
            delete[] constraints;
        };
};
