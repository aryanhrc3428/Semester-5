#include <iostream>

class DynamicStack {
private:
    int* arr;
    int capacity;
    int top;

public:
    DynamicStack() {
        capacity = 2;
        arr = new int[capacity];
        top = -1;
    }

    ~DynamicStack() {
        delete[] arr;
    }

    void push(int value) {
        if (top + 1 == capacity) {
            int newCapacity = capacity * 2;
            int* newArr = new int[newCapacity];

            for (int i = 0; i <= top; ++i) {
                newArr[i] = arr[i];
            }

            delete[] arr;
            arr = newArr;
            capacity = newCapacity;

            std::cout << "Stack full. Resized capacity to " << capacity << "\n";
        }

        arr[++top] = value;
        std::cout << "Pushed " << value << "\n";
    }

    void display() const {
        std::cout << "Stack elements: ";
        for (int i = 0; i <= top; ++i) {
            std::cout << arr[i] << " ";
        }
        std::cout << "\n";
    }
};

int main() {
    DynamicStack stack;

    stack.push(10);
    stack.push(20);
    stack.push(30);
    stack.push(40);
    stack.push(50);

    stack.display();

    return 0;
}