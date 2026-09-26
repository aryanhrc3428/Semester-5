#include <iostream>
#include <vector>
#include <algorithm>

void displayVector(const std::vector<int>& vec) {
    if (vec.empty()) {
        std::cout << "Vector is empty.\n";
        return;
    }
    std::cout << "Vector elements: ";
    for (int val : vec) {
        std::cout << val << " ";
    }
    std::cout << "\n";
}

void rotateLeft(std::vector<int>& vec, int k) {
    if (vec.empty()) return;
    int n = vec.size();
    k = k % n; // Handle cases where k >= vector size
    std::rotate(vec.begin(), vec.begin() + k, vec.end());
}

void rotateRight(std::vector<int>& vec, int k) {
    if (vec.empty()) return;
    int n = vec.size();
    k = k % n; // Handle cases where k >= vector size
    std::rotate(vec.rbegin(), vec.rbegin() + k, vec.rend());
}

int main() {
    int n;
    std::cout << "Enter initial size of vector: ";
    std::cin >> n;

    std::vector<int> vec(n);
    std::cout << "Enter " << n << " elements: ";
    for (int i = 0; i < n; ++i) {
        std::cin >> vec[i];
    }

    int choice;
    do {
        std::cout << "\n==============================\n";
        std::cout << "1. Display the vector\n";
        std::cout << "2. Rotate left by 1 position\n";
        std::cout << "3. Rotate right by 1 position\n";
        std::cout << "4. Rotate left by K positions\n";
        std::cout << "5. Rotate right by K positions\n";
        std::cout << "6. Exit\n";
        std::cout << "Enter your choice: ";
        std::cin >> choice;

        switch (choice) {
            case 1:
                displayVector(vec);
                break;
            case 2:
                rotateLeft(vec, 1);
                std::cout << "Vector rotated left by 1 position.\n";
                break;
            case 3:
                rotateRight(vec, 1);
                std::cout << "Vector rotated right by 1 position.\n";
                break;
            case 4: {
                int k;
                std::cout << "Enter value for K: ";
                std::cin >> k;
                rotateLeft(vec, k);
                std::cout << "Vector rotated left by " << k << " position(s).\n";
                break;
            }
            case 5: {
                int k;
                std::cout << "Enter value for K: ";
                std::cin >> k;
                rotateRight(vec, k);
                std::cout << "Vector rotated right by " << k << " position(s).\n";
                break;
            }
            case 6:
                std::cout << "Exiting program.\n";
                break;
            default:
                std::cout << "Invalid choice! Please select a valid option.\n";
        }
    } while (choice != 6);

    return 0;
}