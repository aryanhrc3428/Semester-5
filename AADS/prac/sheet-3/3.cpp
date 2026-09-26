// Split a vector into even and odd vectors

#include <iostream>
#include <vector>

int main() {
    std::vector<int> original = {12, 5, 8, 13, 22, 9, 1, 4, 10};
    std::vector<int> evens;
    std::vector<int> odds;
    
    for (int i = 0; i < original.size(); ++i) {
        if (original[i] % 2 == 0) {
            evens.push_back(original[i]);
        } else {
            odds.push_back(original[i]);
        }
    }
    
    std::cout << "Even numbers: ";
    for (int i = 0; i < evens.size(); ++i) {
        std::cout << evens[i] << " ";
    }
    std::cout << "\n";
    
    std::cout << "Odd numbers: ";
    for (int i = 0; i < odds.size(); ++i) {
        std::cout << odds[i] << " ";
    }
    std::cout << "\n";
    
    return 0;
}