#include <iostream>

class DynamicStack {
private:
    int* arr;
    int capacity;
    int top;
    int totalOps;

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
        int opCost = 1; // Base cost for insertion

        if (top + 1 == capacity) {
            int copiedItems = top + 1;
            opCost += copiedItems; // Add cost of copying existing items

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

        std::cout << "Pushed: " << value 
                  << " | Cost: " << opCost 
                  << " | Total Ops: " << totalOps 
                  << " | Capacity: " << capacity << "\n";
    }

    int getTotalOps() const {
        return totalOps;
    }
};

int main() {
    DynamicStack stack;

    // Push sequence to demonstrate cost tracking
    for (int i = 1; i <= 6; ++i) {
        stack.push(i * 10);
    }

    return 0;
}