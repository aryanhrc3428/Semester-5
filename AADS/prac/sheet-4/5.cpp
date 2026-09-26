// Merge two sorted sequences

#include <iostream>

void mergeSorted(int arr1[], int size1, int arr2[], int size2, int result[]) {
    int i = 0, j = 0, k = 0;

    while (i < size1 && j < size2) {
        if (arr1[i] <= arr2[j]) {
            result[k++] = arr1[i++];
        } else {
            result[k++] = arr2[j++];
        }
    }

    while (i < size1) {
        result[k++] = arr1[i++];
    }

    while (j < size2) {
        result[k++] = arr2[j++];
    }
}

int main() {
    int arr1[] = {1, 3, 5, 7};
    int size1 = sizeof(arr1) / sizeof(arr1[0]);
    
    int arr2[] = {2, 4, 6, 8, 10};
    int size2 = sizeof(arr2) / sizeof(arr2[0]);
    
    int resultSize = size1 + size2;
    int* result = new int[resultSize];
    
    mergeSorted(arr1, size1, arr2, size2, result);
    
    std::cout << "Merged sorted sequence: ";
    for (int i = 0; i < resultSize; ++i) {
        std::cout << result[i] << " ";
    }
    std::cout << "\n";
    
    delete[] result;
    return 0;
}