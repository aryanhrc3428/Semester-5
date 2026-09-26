#include <iostream>
#include <vector>
#include <algorithm>

void removeDuplicates(std::vector<int>& nums) {
    auto it = std::unique(nums.begin(), nums.end());
    nums.erase(it, nums.end());
}

int main() {
    std::vector<int> nums = {1, 1, 2, 2, 3, 4, 4, 4, 5, 5};

    std::cout << "Original vector: ";
    for (int num : nums) {
        std::cout << num << " ";
    }
    std::cout << "\n";

    removeDuplicates(nums);

    std::cout << "Vector after removing duplicates: ";
    for (int num : nums) {
        std::cout << num << " ";
    }
    std::cout << "\n";

    return 0;
}