// Find the Longest Increasing Subsequence (LIS)

#include <iostream>

int longestIncreasingSubsequence(int arr[], int n) {
    if (n == 0) return 0;

    int* dp = new int[n];
    int maxLIS = 1;

    for (int i = 0; i < n; ++i) {
        dp[i] = 1; 
        for (int j = 0; j < i; ++j) {
            if (arr[i] > arr[j] && dp[i] < dp[j] + 1) {
                dp[i] = dp[j] + 1;
            }
        }
        if (dp[i] > maxLIS) {
            maxLIS = dp[i];
        }
    }

    delete[] dp;
    return maxLIS;
}

int main() {
    int arr[] = {10, 22, 9, 33, 21, 50, 41, 60, 80};
    int n = sizeof(arr) / sizeof(arr[0]);

    int result = longestIncreasingSubsequence(arr, n);
    
    std::cout << "Sequence: ";
    for (int i = 0; i < n; ++i) std::cout << arr[i] << " ";
    std::cout << "\nLength of LIS is: " << result << "\n";

    return 0;
}