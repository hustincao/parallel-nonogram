#include "utils.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

int main() {
    Game game;

    game.load_game("tests/0");

    // for(int i = 0; i < game.len_constraints[0]; i++){
    //     std::cout<<game.constraints[0][i] << " ";
    // }
    // std::cout<<"\n";

    // for(unsigned int i = 0; i < game.width; i++){
    //     game.get_board(0,i) = 0;
    //     std::cout << game.get_board(0,i) << " ";
    // }

    // game.print_constraints();
    // game.print_constraints();
    game.print_board();
    game.print_solution();
    game.free_dynamic_memory();

    return 0;
}