// Count the occurrences of each element in a vector

#include <iostream>
#include <vector>

void countFrequencies(const std::vector<int>& vec) {
    std::vector<bool> visited(vec.size(), false);
    
    for (int i = 0; i < vec.size(); ++i) {
        if (visited[i]) {
            continue;
        }
        
        int count = 1;
        for (int j = i + 1; j < vec.size(); ++j) {
            if (vec[i] == vec[j]) {
                visited[j] = true;
                count++;
            }
        }
        
        std::cout << "Element " << vec[i] << " occurs " << count << " time(s)\n";
    }
}

int main() {
    std::vector<int> vec = {5, 2, 5, 8, 2, 5, 1, 8, 9};
    
    countFrequencies(vec);
    
    return 0;
}