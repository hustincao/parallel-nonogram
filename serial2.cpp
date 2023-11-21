#include "utils.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

struct Block {
    unsigned int min_index;
    unsigned int max_index;
    unsigned int count;
    Block *previous;
    Block *next;
};

int main() {
    Game game;
    std::vector<Block> blocks;

    game.load_game("tests/0");
    for (int i = 0; i < game.len_constraints[0]; i++) {
        blocks.push_back(Block{0, 5, game.constraints[0][i], nullptr, nullptr});
        std::cout << game.constraints[0][i] << " ";
    }
    std::cout << "\n";

    for (int i = 0; i < blocks.size(); i++) {
        std::cout << blocks[i].count << " ";
    }
    std::cout << "\n";

    // game.print_board();
    // game.print_solution();
    game.free_dynamic_memory();

    return 0;
}