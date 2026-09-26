// Brute Force Pattern Matching with Comparison Counter

#include <iostream>
#include <string>
#include <vector>

int totalComparisons = 0;

std::vector<int> bruteForceSearch(const std::string& T, const std::string& P) {
    std::vector<int> matchIndices;
    int n = T.length();
    int m = P.length();

    if (m == 0 || n < m) {
        return matchIndices;
    }

    for (int i = 0; i <= n - m; ++i) {
        int j = 0;
        while (j < m) {
            totalComparisons++;
            if (T[i + j] != P[j]) {
                break;
            }
            j++;
        }
        if (j == m) {
            matchIndices.push_back(i);
        }
    }

    return matchIndices;
}

int main() {
    std::string T = "ABABDABACDABABCABAB";
    std::string P = "ABABCABAB";
    
    totalComparisons = 0;
    
    std::vector<int> indices = bruteForceSearch(T, P);
    
    std::cout << "Text: " << T << "\n";
    std::cout << "Pattern: " << P << "\n";
    std::cout << "Match indices: ";
    if (indices.empty()) {
        std::cout << "None";
    } else {
        for (int i = 0; i < indices.size(); ++i) {
            std::cout << indices[i] << " ";
        }
    }
    std::cout << "\nTotal character comparisons: " << totalComparisons << "\n";
    
    return 0;
}