#include <iostream>

class DynamicStack {
private:
    int* arr;
    int capacity;
    int top;
    long long totalOps;

public:
    DynamicStack() {
        capacity = 2;
        arr = new int[capacity];
        top = -1;
        totalOps = 0;
    }

    ~DynamicStack() {
        delete[] arr;
    }

    void push(int value) {
        int opCost = 1;

        if (top + 1 == capacity) {
            int copiedItems = top + 1;
            opCost += copiedItems;

            int newCapacity = capacity * 2;
            int* newArr = new int[newCapacity];

            for (int i = 0; i <= top; ++i) {
                newArr[i] = arr[i];
            }

            delete[] arr;
            arr = newArr;
            capacity = newCapacity;
        }

        arr[++top] = value;
        totalOps += opCost;
    }

    long long getTotalOps() const {
        return totalOps;
    }
};

int main() {
    DynamicStack stack;
    const int numPushes = 1000;

    for (int i = 1; i <= numPushes; ++i) {
        stack.push(i);
    }

    long long totalCost = stack.getTotalOps();
    double averageCost = static_cast<double>(totalCost) / numPushes;

    std::cout << "Total Pushes: " << numPushes << "\n";
    std::cout << "Total Cost (Operations): " << totalCost << "\n";
    std::cout << "Average Cost per Push: " << averageCost << "\n";

    return 0;
}