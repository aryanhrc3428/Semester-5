// Find the common elements between two vectors

#include <iostream>
#include <vector>

bool isPresent(const std::vector<int>& vec, int element) {
    for (int i = 0; i < vec.size(); ++i) {
        if (vec[i] == element) {
            return true;
        }
    }
    return false;
}

std::vector<int> findCommonElements(const std::vector<int>& v1, const std::vector<int>& v2) {
    std::vector<int> common;
    
    for (int i = 0; i < v1.size(); ++i) {
        for (int j = 0; j < v2.size(); ++j) {
            if (v1[i] == v2[j]) {
                if (!isPresent(common, v1[i])) {
                    common.push_back(v1[i]);
                }
                break;
            }
        }
    }
    
    return common;
}

int main() {
    std::vector<int> vec1 = {1, 4, 5, 9, 2, 4};
    std::vector<int> vec2 = {9, 2, 4, 8, 10};
    
    std::vector<int> common = findCommonElements(vec1, vec2);
    
    std::cout << "Common elements: ";
    for (int i = 0; i < common.size(); ++i) {
        std::cout << common[i] << " ";
    }
    std::cout << "\n";
    
    return 0;
}