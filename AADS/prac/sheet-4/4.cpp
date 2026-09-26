// Check whether a sequence is a palindrome

#include <iostream>

bool isPalindrome(int arr[], int size) {
    int left = 0;
    int right = size - 1;
    
    while (left < right) {
        if (arr[left] != arr[right]) {
            return false;
        }
        left++;
        right--;
    }
    return true;
}

int main() {
    int seq1[] = {1, 2, 3, 2, 1};
    int size1 = sizeof(seq1) / sizeof(seq1[0]);
    
    int seq2[] = {1, 2, 3, 4, 5};
    int size2 = sizeof(seq2) / sizeof(seq2[0]);
    
    std::cout << "Sequence 1 is palindrome: " 
              << (isPalindrome(seq1, size1) ? "Yes" : "No") << "\n";
              
    std::cout << "Sequence 2 is palindrome: " 
              << (isPalindrome(seq2, size2) ? "Yes" : "No") << "\n";

    return 0;
}