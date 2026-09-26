// Write a program to implement KMP string pattern matching algorithm, output must include total number of comparisons made during execution.

#include <iostream>
#include <vector>
#include <string>

int totalComparisons = 0;

std::vector<int> computeLPS(const std::string& P) {
    int m = P.length();
    std::vector<int> lps(m, 0);
    int len = 0;
    int i = 1;

    while (i < m) {
        totalComparisons++; 
        if (P[i] == P[len]) {
            len++;
            lps[i] = len;
            i++;
        } else {
            if (len != 0) {
                len = lps[len - 1];
            } else {
                lps[i] = 0;
                i++;
            }
        }
    }
    return lps;
}

std::vector<int> KMPSearch(const std::string& T, const std::string& P) {
    std::vector<int> matchIndices;
    int n = T.length();
    int m = P.length();

    if (m == 0 || n < m) {
        return matchIndices;
    }

    std::vector<int> lps = computeLPS(P);

    int i = 0; 
    int j = 0; 

    while (i < n) {
        totalComparisons++; 
        if (T[i] == P[j]) {
            i++;
            j++;
            
            if (j == m) {
                matchIndices.push_back(i - j);
                j = lps[j - 1];
            }
        } else {
            if (j != 0) {
                j = lps[j - 1];
            } else {
                i++;
            }
        }
    }

    return matchIndices;
}

int main() {
    std::string T = "ABABDABACDABABCABAB";
    std::string P = "ABABCABAB";
    
    totalComparisons = 0;
    
    std::vector<int> indices = KMPSearch(T, P);
    
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