#include <iostream>
#include <limits>
using namespace std;

template<class T>
class Vector {
    int size;
    int capacity;
    T* arr;

    void doublingSystem() {
        cout << "-> Capacity Exceeded. Time to Double the Capacity!" << endl;
        capacity *= 2;
        
        T* temp = new T[capacity];
        for (int i = 0; i < size; i++) {
            *(temp + i) = *(arr + i);
        }
        delete[] arr; 
        arr = temp;   
    }

public:
    ~Vector() {
        delete[] arr;
    }

    Vector() {
        size = 0;
        capacity = 1;
        arr = new T[capacity];
    }

    Vector(int x) {
        if (x < 0) {
            size = 0;
            capacity = 1;
            arr = new T[capacity];
            return;
        }
        size = x;
        capacity = x;
        arr = new T[capacity];
    }

    Vector(int x, T* list) {
        if (list == nullptr) {
            throw invalid_argument("List is a nullptr");
        }
        if (x < 0) {
            size = 0;
            capacity = 1;
            arr = new T[capacity];
            return;
        }

        size = x;
        capacity = x;
        arr = new T[capacity];

        for (int i = 0; i < x; i++) *(arr + i) = *(list + i);
    }

    T at(int i) {
        if (i < 1 || i > size) {
            cout << "-> Error: Position out of bounds!" << endl;
            return -1; 
        }
        return *(arr + i - 1);
    }

    void insert(int i, T e) {
        if (i < 1 || i > size + 1) {
            cout << "-> Error: Position out of bounds!" << endl;
            return;
        }
        if (size == capacity) doublingSystem();

        for (int it = size; it > i - 1; it--) {
            *(arr + it) = *(arr + it - 1);
        }
        
        *(arr + i - 1) = e;
        size++;
    }

    void erase(int i) { 
        if (i < 1 || i > size) {
            cout << "-> Error: Position out of bounds!" << endl;
            return;
        }
        if (size == 0) {
            cout << "-> Error: Vector is empty!" << endl;
            return;
        }

        for (int it = i - 1; it < size - 1; it++) {
            *(arr + it) = *(arr + it + 1);
        }
        size--;
    }

    void set(int i, T e) {
        if (i < 1 || i > size) {
            cout << "-> Error: Position out of bounds!" << endl;
            return;
        }
        *(arr + i - 1) = e;
    }

    void push_back(T e) {
        if (size == capacity) doublingSystem();
        *(arr + size) = e;
        size++;
    }

    void pop_back() {
        if (size == 0) {
            cout << "-> Error: Vector is already empty!" << endl;
            return;
        }
        size--;
    }

    void print() {
        cout << "Vector: [ ";
        for (int i = 0; i < size; i++) {
            cout << *(arr + i) << " ";
        }
        cout << "] (Size: " << size << ", Capacity: " << capacity << ")\n";
    }
};

int main() {
    Vector<int> v;
    int choice, pos, value;

    while (true) {
        cout << "\n=== Custom Vector Menu (1-Based Positions) ===\n";
        cout << "1. Push Back (push_back)\n";
        cout << "2. Pop Back (pop_back)\n";
        cout << "3. Insert at Position (insert)\n";
        cout << "4. Erase at Position (erase)\n";
        cout << "5. Set Element at Position (set)\n";
        cout << "6. Get Element at Position (at)\n";
        cout << "7. Print Vector\n";
        cout << "8. Exit\n";
        cout << "Enter your choice (1-8): ";

        if (!(cin >> choice)) {
            cout << "Invalid input! Please enter a number.\n";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            continue;
        }

        if (choice == 8) {
            cout << "Exiting program...\n";
            break;
        }

        switch (choice) {
            case 1:
                cout << "Enter value to push back: ";
                cin >> value;
                v.push_back(value);
                v.print();
                break;

            case 2:
                v.pop_back();
                v.print();
                break;

            case 3:
                cout << "Enter position (1 to " << (v.at(1) == -1 ? 1 : 999) << /*placeholder*/ ") to insert at: ";
                cin >> pos;
                cout << "Enter value to insert: ";
                cin >> value;
                v.insert(pos, value);
                v.print();
                break;

            case 4:
                cout << "Enter position to erase (1-based): ";
                cin >> pos;
                v.erase(pos);
                v.print();
                break;

            case 5:
                cout << "Enter position to set (1-based): ";
                cin >> pos;
                cout << "Enter new value: ";
                cin >> value;
                v.set(pos, value);
                v.print();
                break;

            case 6:
                cout << "Enter position to retrieve (1-based): ";
                cin >> pos;
                value = v.at(pos);
                if (value != -1) {
                    cout << "-> Value at position " << pos << " is: " << value << "\n";
                }
                break;

            case 7:
                v.print();
                break;

            default:
                cout << "Invalid choice! Please select an option between 1 and 8.\n";
        }
    }

    return 0;
}