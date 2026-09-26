// Remove duplicates in-place from a sorted vector

#include <iostream>

void insertElement(int arr[], int& size, int pos, int val, int capacity) {
    if (pos < 0 || pos > size || size >= capacity) {
        std::cout << "Invalid position or array is full.\n";
        return;
    }
    for (int i = size; i > pos; --i) {
        arr[i] = arr[i - 1];
    }
    arr[pos] = val;
    size++;
}

void deleteElement(int arr[], int& size, int pos) {
    if (pos < 0 || pos >= size) {
        std::cout << "Invalid position.\n";
        return;
    }
    for (int i = pos; i < size - 1; ++i) {
        arr[i] = arr[i + 1];
    }
    size--;
}

int getLength(int size) {
    return size;
}

int main() {
    int arr[100];
    int size = 0;
    int capacity = 100;

    insertElement(arr, size, 0, 10, capacity);
    insertElement(arr, size, 1, 20, capacity);
    insertElement(arr, size, 1, 15, capacity); 

    std::cout << "Array after insertions: ";
    for (int i = 0; i < size; ++i) std::cout << arr[i] << " ";
    std::cout << "\nLength: " << getLength(size) << "\n";

    deleteElement(arr, size, 1);

    std::cout << "Array after deletion at index 1: ";
    for (int i = 0; i < size; ++i) std::cout << arr[i] << " ";
    std::cout << "\nLength: " << getLength(size) << "\n";

    return 0;
}