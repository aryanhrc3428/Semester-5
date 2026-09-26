// LPS (Longest Prefix Suffix) Array Construction

#include <iostream>
#include <string>
#include <vector>

std::vector<int> computeLPSArray(const std::string& P) {
    int m = P.length();
    std::vector<int> lps(m, 0);
    
    if (m == 0) {
        return lps;
    }
    
    int len = 0;
    int i = 1;
    
    while (i < m) {
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

int main() {
    std::string pattern1 = "AAAA";
    std::string pattern2 = "ABCDE";
    std::string pattern3 = "AABAACAABAA";
    std::string pattern4 = "AAACAAAAAC";

    std::vector<std::string> patterns = {pattern1, pattern2, pattern3, pattern4};

    for (int p = 0; p < patterns.size(); ++p) {
        std::vector<int> lps = computeLPSArray(patterns[p]);
        
        std::cout << "Pattern: " << patterns[p] << "\nLPS: ";
        for (int i = 0; i < lps.size(); ++i) {
            std::cout << lps[i] << " ";
        }
        std::cout << "\n\n";
    }

    return 0;
}